from fastapi import FastAPI
app = FastAPI()

@app.post("/data")
async def process_data(data: str):
    # prediction
    prediction = None
    return {"result" : None}
