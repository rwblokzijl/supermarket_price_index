#!/usr/bin/env python3

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from query import get_query

import json
import csv

from typing import *

def persist_to_file(file_name):
    def decorator(original_func):
        def new_func():
            try:
                cache = json.load(open(file_name, 'r'))
            except (IOError, ValueError):
                cache = {}
            if not cache:
                cache = original_func()
                json.dump(cache, open(file_name, 'w'))
            return cache

        return new_func

    return decorator

def get_products(client, ptype, cursor="") -> List:
    print("NEW PAGE")
    query    = gql(get_query(ptype, cursor))
    result   = client.execute(query)
    products = result["productType"]["products"]["edges"]

    if result["productType"]["products"]["pageInfo"]["hasNextPage"]:
        cursor = result["productType"]["products"]["pageInfo"]["endCursor"]
        return products + get_products(client, ptype, cursor=cursor)
    else:
        return products

def get_product_types(client, offset=""):
    query = gql(
        """
        query {
          productTypes(first: 100) {
            edges {
              node {
                id
              }
            }
          }
        }
        """)
    result = client.execute(query)
    return [edge["node"]["id"] for edge in result["productTypes"]["edges"]]

@persist_to_file("products.json")
def get_all_products():
    client = Client(transport=RequestsHTTPTransport(url="https://flink.grocery-backend.nl"), fetch_schema_from_transport=True)
    productTypes = get_product_types(client)
    products = []
    for t in productTypes:
        products += get_products(client, t)
    print(products)
    return products

def clean_product(product):
    ean_values = [a for a in product["node"]["attributes"] if a["attribute"]["name"] == "EAN"][0]["values"]#[0]["name"],
    if not ean_values:
        ean = None
    else:
        ean = ean_values[0]["name"]

    category = product["node"]["category"]
    if not category:
        category = None
        subcategory = None
    elif not category["parent"]:
        category = product["node"]["category"]["name"]
        subcategory = None
    elif not category["parent"]["parent"]:
        category = product["node"]["category"]["parent"]["name"]
        subcategory = product["node"]["category"]["name"]
    else:
        assert False, "3 layers of category"

    return {
            "name": product["node"]["name"],
            "ean": ean,
            "category": category,
            "subcategory": subcategory,
            "price_gross": product["node"]["pricing"]["priceRange"]["start"]["gross"]["amount"],
            "price_net":   product["node"]["pricing"]["priceRange"]["start"]["net"]["amount"],
            "price_tax":   product["node"]["pricing"]["priceRange"]["start"]["tax"]["amount"],
            }

def main():
    raw_products = get_all_products()
    print(len(raw_products))
    products = [clean_product(product) for product in raw_products]
    with open('prices.csv', 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file,
                fieldnames=products[0].keys(),

                )
        fc.writeheader()
        fc.writerows(products)


if __name__ == "__main__":
    main()

