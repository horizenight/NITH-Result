from fastapi import FastAPI,HTTPException
from main import main , show_data
from mangum import Mangum 


from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/update_result")
async def update_result():
    process = await main("config.json" , 1 , True)
    return {"Result status": "Updated"}




# @app.get("/show_result")
# async def result_result():
#     mongo_data  = show_data()
#     print(mongo_data[:])
#     print(len(mongo_data[0]))
#     return {"Result status": "working"}




