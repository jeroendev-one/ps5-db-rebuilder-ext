#!/usr/bin/env python
import argparse
import requests
import json

def make_request(product_id):
    url = f"https://web.np.playstation.com/api/graphql/v1/op"
    headers = {
        'x-psn-store-locale-override': 'en-gb'
    }
    payload = {
        'operationName': 'metGetProductById',
        'variables': f'{{"productId":"{product_id}"}}',
        'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"a128042177bd93dd831164103d53b73ef790d56f51dae647064cb8f9d9fc9d1a"}}'
    }

    # Send GET request with parameters
    response = requests.get(url, headers=headers, params=payload)

    # Check if request was successful (status code 200)
    if response.status_code == 200:
        json_response = response.json()
        # Access the desired field in the JSON response
        if 'data' in json_response and 'productRetrieve' in json_response['data'] and 'concept' in json_response['data']['productRetrieve']:
            concept_id = json_response['data']['productRetrieve']['concept']['id']
            print("Concept ID:", concept_id)
        else:
            print("The required field was not found in the response")
    else:
        print("Request failed")
        print("Status code:", response.status_code)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve concept ID for a PlayStation product.")
    parser.add_argument("product_id", type=str, help="PlayStation product ID (e.g., UP0001-CUSA09311_00-GAME000000000000)")

    args = parser.parse_args()
    make_request(args.product_id)

