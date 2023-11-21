#!/usr/bin/env python
import argparse
import requests

parser = argparse.ArgumentParser(description="Retrieve concept ID for a PlayStation product.")
parser.add_argument("product_id", type=str, help="PlayStation product ID (e.g., UP0001-CUSA09311_00-GAME000000000000)")
args = parser.parse_args()

def make_request(product_id):
    regions = ['en-us', 'en-gb']

    for region in regions:
        #print(f"Trying region: {region}")
        url = f"https://web.np.playstation.com/api/graphql/v1/op"
        headers = {'x-psn-store-locale-override': region}
        payload = {'operationName': 'metGetProductById', 'variables': f'{{"productId":"{product_id}"}}', 'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"a128042177bd93dd831164103d53b73ef790d56f51dae647064cb8f9d9fc9d1a"}}'}

        response = requests.get(url, headers=headers, params=payload)

        if response.status_code != 200:
            print("Request failed")
            print("Status code:", response.status_code)
            continue

        json_response = response.json()
        if 'errors' in json_response and any('Product not available' in error['message'] for error in json_response['errors']):
            #print("Product not available in this region.")
            continue

        content_id = json_response.get('data', {}).get('productRetrieve', {}).get('concept', {}).get('id')
        if content_id:
            print(content_id)
            break

    else:
        print("Content ID not found for the provided product ID")

# Call the function with the arguments
make_request(args.product_id)