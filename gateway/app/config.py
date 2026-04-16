import os

from dotenv import load_dotenv

load_dotenv()

SERVICES = {
    "users": os.getenv("USERS_URL"),
    "inventory": os.getenv("INVENTORY_URL"),
}