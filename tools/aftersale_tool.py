from tools.db import fetch_one

def query_after_sale(order_id: str):
    return fetch_one("after_sales", order_id)
