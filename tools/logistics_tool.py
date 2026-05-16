from tools.db import fetch_one

def query_logistics(order_id: str):
    return fetch_one("logistics", order_id)
