import argparse
import asyncio
import json
import os

import aiohttp
import exrex
import pymongo
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from enum import Enum


class Singleton(type):
 
    """ Singleton Design Pattern  """
 
    _instance = {}
 
    def __call__(cls, *args, **kwargs):
 
        """ if instance already exist dont create one  """
 
        if cls not in cls._instance:
            cls._instance[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            return cls._instance[cls]


class MongoDbSettings(object):
    def __init__(self,
                 connection_string,
                 database_name,
                 collection_name):
        self.connection_string = connection_string
        self.collection_name = collection_name
        self.database_name = database_name


class MongoDB(metaclass=Singleton):
 
    def __init__(self, mongo_db_settings):
        self.mongo_db_settings = mongo_db_settings
        if type(self.mongo_db_settings).__name__ != "MongoDbSettings":
            raise Exception("Please mongo_db_settings  pass correct Instance")
 
        self.client = pymongo.MongoClient(self.mongo_db_settings.connection_string)
        self.cursor = self.client[self.mongo_db_settings.database_name][
            self.mongo_db_settings.collection_name
        ]
 
    def get_data(self, query={}, mongo_batch_size=100):
 
        # 2000
        total_count = self.cursor.count_documents(filter=query)
 
        # 2000//100
        total_pages = total_count // mongo_batch_size
 
        page_size = mongo_batch_size
 
        if total_count % mongo_batch_size != 0:
            total_pages += 1
 
        for page_number in range(1, total_pages + 1):
 
            skips = page_size * (page_number - 1)
            cursor = self.cursor.find(query).skip(skips).limit(page_size)
            yield [x for x in cursor]
 

 
class Connector(Enum):
    load_dotenv(dotenv_path="../.env")
    MONGODB_QA = MongoDB(
        mongo_db_settings=MongoDbSettings(
            connection_string=os.getenv("MONGO_URL"),
           
            database_name=os.getenv("MONGO_DB"),
            collection_name="RESULT_SHORT",
        )
    )


def show_data():
    connector  = Connector.MONGODB_QA.value
 
    query = {}
    mongo_data = connector.get_data(query=query)
 
    while True:
        try:
            data = next(mongo_data)
        except StopIteration:
            break
        except Exception as e:
            continue
    return data
   



async def scrape(session, url, rollno, retries):
    try:
        async with session.post(url, data={"RollNumber": rollno}) as resp:
            soup = BeautifulSoup(await resp.text(), "lxml")
            res_table = soup.find_all("table")
            if len(res_table) < 4:
                if retries == 0:
                    return {
                        "_id": rollno,
                        "error": "NA",
                    }

                return await scrape(session, url, rollno, retries - 1)

            results = soup.select("tr[class='thcolor']")
            sem_result = {}
            for id, result in enumerate(results):
                tmp = []
                result = result.find_next_siblings()
                for r in result:
                    record = r.find_all("td")
                    tmp.append([i.text.strip() for i in record[1:]])
                sem_result[f"{id+1}"] = tmp

            res_data = res_table[-2].find_all("td")
            return {
                "_id": rollno,
                "name": res_table[1].find_all("td")[1].find_all("p")[1].text.strip(),
                "sgpi": float(res_data[1].text.split("=")[1].strip()),
                "cgpi": float(res_data[3].text.split("=")[1].strip()),
                "result": sem_result,
            }

    except Exception as e:
        return {
            "_id": rollno,
            "error": str(e),
        }


async def save_result(mongoDB, batch, data, save_mongo):
    data, results = [i for i in data if "error" not in i], []
   
    if len(data) == 0:
        print("Nothing scraped")
        return 


    with open(f"results/result-{batch}.json", "w") as f:
        json.dump(data, f)

    for i in data:
        results.append(
            {
                "_id": i["_id"],
                "result": i.pop("result"),
            }
        )


    if save_mongo:
        
        mongoCol = mongoDB["RESULT_SHORT"].drop()
        mongoCol = mongoDB["RESULT_SHORT"]
        mongoCol.insert_many(data)
       
        
        mongoCol = mongoDB["RESULT_LONG"].drop()
        mongoCol = mongoDB["RESULT_LONG"]
        mongoCol.insert_many(results)
       
       
      


async def main(config_path, retries, save_mongo):
    mongoClient = pymongo.MongoClient(os.getenv("MONGO_URL"))
    mongoDB = mongoClient[os.getenv("MONGO_DB")]
    config = json.load(open(config_path, "r"))

    for batch, conf in config.items():
        print(f"Scraping started for {batch}. Please wait...")
        rollGen = exrex.generate(conf["regex"])
        async with aiohttp.ClientSession() as session:
            tasks = []
            for roll in rollGen:
                task = asyncio.ensure_future(
                    scrape(session, conf["url"], roll, retries)
                )
                tasks.append(task)

            await save_result(mongoDB, batch, await asyncio.gather(*tasks), save_mongo)


if __name__ == "__main__":
    # Parser Config
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to config", default="config.json")
    parser.add_argument("-r", "--retries", help="Total retries", default=1)
    parser.add_argument("-s", "--save", help="Save to MongoDB", action="store_true")
    args = parser.parse_args()

    load_dotenv(dotenv_path="../.env")
    isExist = os.path.exists("results")
    if not isExist:
        os.makedirs("results")

    print(args.config, args.retries , args.save)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(args.config, args.retries, args.save))
    
    loop.close()
