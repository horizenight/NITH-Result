import argparse
import asyncio
import json
import os

import aiohttp
import exrex
import pymongo
from bs4 import BeautifulSoup
from dotenv import load_dotenv


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
        mongoCol = mongoDB["RESULT_SHORT"]
        mongoCol.insert_many(data)
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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(args.config, args.retries, args.save))
    loop.close()
