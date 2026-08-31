from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Smart task manager API is Running"}