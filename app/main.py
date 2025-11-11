from fastapi import FastAPI, UploadFile, File


app = FastAPI()

@app.get("/ping")
async def ping():
  return {"status": "ok"}

