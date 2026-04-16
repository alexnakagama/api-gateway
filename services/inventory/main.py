from fastapi import FastAPI

app = FastAPI()

@app.get("/inventory")
async def get_inventory():
    return [
        {"id": 1, "item": "product A", "stock": 10},
        {"id:": 2, "item": "product B", "stock": 5},
    ]