from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/api/v1/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
