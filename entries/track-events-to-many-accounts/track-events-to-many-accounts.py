# Send the same event to multiple accounts
import requests
import base64
import json

# List of accounts to track event to
accounts = ['abc123','123abc','def456','456def']

url = "https://a.klaviyo.com/api/track"

for account in accounts:
    # Payload to track
    payload = {
        "token" : account,
        "event" : "Started Checkout - Template Training",
        "customer_properties" : {
            "$email" : "test.person@test.com",
            "$first_name" : "Coolfirstname",
            "$last_name" :"Sweetlastname"
        },
        "properties" : {
            "$event_id": "1000123_1387299426",
            "$value": 39.98,
            "ItemNames": ["Winnie the Pooh", "A Tale of Two Cities", "book3"],
            "CheckoutURL": "http://www.example.com/path/to/checkout",
            "Items": [{
                    "ProductID": "1111",
                    "SKU": "WINNIEPOOH",
                    "ProductName": "Winnie the Pooh",
                    "Quantity": 1,
                    "ItemPrice": 14.99,
                    "SalePrice": 9.99,
                    "RowTotal": 9.99,
                    "ProductURL": "http://www.example.com/path/to/product",
                    "ImageURL": "http://www.example.com/path/to/product/image.png",
                    "ProductCategories": ["Fiction", "Children"]
                },
                {
                    "ProductID": "1112",
                    "SKU": "TALEOFTWO",
                    "ProductName": "A Tale of Two Cities",
                    "Quantity": 1,
                    "ItemPrice": 19.99,
                    "SalePrice": 19.99,
                    "RowTotal": 19.99,
                    "ProductURL": "http://www.example.com/path/to/product2",
                    "ImageURL": "http://www.example.com/path/to/product/image2.png",
                    "ProductCategories": ["Fiction", "Classics"]
                },
                {
                    "ProductID": "1113",
                    "SKU": "book3",
                    "ProductName": "book3",
                    "Quantity": 2,
                    "ItemPrice": 19.99,
                    "SalePrice": 10.00,
                    "RowTotal": 10.00,
                    "ProductURL": "http://www.example.com/path/to/product3",
                    "ImageURL": "http://www.example.com/path/to/product/image3.png",
                    "ProductCategories": ["Fiction", "Young Adult"]
                }]
            }
    }


    urlSafeEncodedBytes = base64.urlsafe_b64encode(json.dumps(payload).encode('utf-8'))
    #print urlSafeEncodedBytes

    # Set URL parameters
    querystring = {"data":urlSafeEncodedBytes}

    # Send request
    response = requests.request("GET", url, params=querystring)
    print(response.text)
