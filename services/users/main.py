from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
async def get_users():
    return [{"id": 1, "name": "user example"}]