from tools.db import fetch_one

def query_refund(order_id: str):
    return fetch_one("refunds", order_id)
