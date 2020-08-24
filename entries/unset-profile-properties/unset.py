import requests
import json

# fill in the blank with your list/segment id
LIST_ID = " "

# fill in the blank with your private api
PRIVATE_API = " "

# replace $first_name/$last_name or add any properties you want unset
profiles_querystring = {
  "$unset": "[\"$first_name\", \"$last_name\"]", 
  "api_key": PRIVATE_API
  }

list_querystring = {
  "api_key": PRIVATE_API
  }

list_url = "https://a.klaviyo.com/api/v2/group/"+LIST_ID+"/members/all"

profiles_url = "https://a.klaviyo.com/api/v1/person/"

profiles_arr = []
 
headers = { 
  "content-type": "application/json",
  "cache-control": "no-cache",
  }
 
response = requests.request("GET", list_url, headers=headers, params=list_querystring).json()

# append profile ids to profiles_arr
for record in response["records"]:
	profiles_arr.append(record["id"])

# unset profile properties
for profileid in range(len(profiles_arr)):
    response = requests.request("PUT", profiles_url+profiles_arr[profileid], headers=headers, params=profiles_querystring)
    
    print(response.text)