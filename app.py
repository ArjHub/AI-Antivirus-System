from fastapi import FastAPI, UploadFile, File
import uvicorn
app = FastAPI()

@app.post("/file")
async def file(file: UploadFile = File(...)):
    # malware file to check!

    # logic & data sent to respective API
    response = None
    return {"result" : 1}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)