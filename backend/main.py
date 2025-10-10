from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello-world")
def hello_world():
    return {"data": "Hello World"}

