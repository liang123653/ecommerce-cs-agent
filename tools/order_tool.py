from tools.db import fetch_one

def query_order(order_id: str):
    return fetch_one("orders", order_id)
