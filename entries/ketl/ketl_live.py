from datetime import datetime

import importlib
from ketl import KetlClient
import ketl_keys

# Reload library if running live from terminal and making changes
# importlib.reload(ketl)

############ EXAMPLE ############
# Set date range to sync
"""
since_datetime = '2020-06-23 00:00:00'  # datetime string
until_datetime = '2020-06-26 00:00:00'  # datetime string
since = datetime.timestamp(datetime.strptime(since_datetime, '%Y-%m-%d %H:%M:%S'))  # unix timestamp for lower bound
until = datetime.timestamp(datetime.strptime(until_datetime, '%Y-%m-%d %H:%M:%S'))  # unix timestamp for upper bound
"""

############ EXAMPLE ############
# Specify a filter for properties to retrieve and save
"""
profile_properties_to_save = ['email']
event_properties_to_save = ['*']
"""

############ EXAMPLE ############
# Set the "from" and "to" keys for the process to be run and initialize the client for both
"""
FROM_KLAVIYO_PUBLIC_API_KEY = ketl_keys.KLAVIYO_DUMMY_PUBLIC_API_KEY  # 'abc123'
FROM_KLAVIYO_PRIVATE_API_KEY = ketl_keys.KLAVIYO_DUMMY_PRIVATE_API_KEY  # 'pk_something'

TO_KLAVIYO_PUBLIC_API_KEY = ketl_keys.KLAVIYO_DUMMY_PUBLIC_API_KEY  # 'def456'
TO_KLAVIYO_PRIVATE_API_KEY = ketl_keys.KLAVIYO_DUMMY_PRIVATE_API_KEY  # 'pk_somethingelse'

ketl_client_from = KetlClient(public_api_key=FROM_KLAVIYO_PUBLIC_API_KEY, private_api_key=FROM_KLAVIYO_PRIVATE_API_KEY)
ketl_client_to = KetlClient(public_api_key=TO_KLAVIYO_PUBLIC_API_KEY, private_api_key=TO_KLAVIYO_PRIVATE_API_KEY)
"""

############ EXAMPLE ############
# Account Migration: Pull "Active on Site" and "Viewed Product" metrics and specific profile properties from old
#  Hello Molly account, filter for specific profiles (only US cusotmers) and retrack to new account

FROM_KLAVIYO_PUBLIC_API_KEY = None  # 'abc123'
FROM_KLAVIYO_PRIVATE_API_KEY = ketl_keys.HELLO_MOLLY_FROM_PRIVATE_API_KEY  # 'pk_something'

TO_KLAVIYO_PUBLIC_API_KEY = ketl_keys.HELLO_MOLLY_TO_PUBLIC_API_KEY  # 'def456'
TO_KLAVIYO_PRIVATE_API_KEY = None  # 'pk_somethingelse'

ketl_client_from = KetlClient(public_api_key=FROM_KLAVIYO_PUBLIC_API_KEY, private_api_key=FROM_KLAVIYO_PRIVATE_API_KEY)
ketl_client_to = KetlClient(public_api_key=TO_KLAVIYO_PUBLIC_API_KEY, private_api_key=TO_KLAVIYO_PRIVATE_API_KEY)

# 1) pull segment of desired profiles to migrate and generate a csv of emails or KIDs
# 2) pull all data from desired metrics into json array files
#  MffU3m - Active on Site
#  LX2awW - Viewed Product
# 3) filter json files for correct emails from CSV and correct profile properties from desired set
# 4) save as new json array
# 5) push data as Track requests into new account

########################################################################################################################################
since_datetime = '2020-06-26 00:00:00'  # datetime string
until_datetime = '2020-06-26 01:00:00'  # datetime string
since = int(datetime.timestamp(datetime.strptime(since_datetime, '%Y-%m-%d %H:%M:%S')))  # unix timestamp for lower bound
until = int(datetime.timestamp(datetime.strptime(until_datetime, '%Y-%m-%d %H:%M:%S')))  # unix timestamp for upper bound
FROM_KLAVIYO_PUBLIC_API_KEY = None  # 'abc123'
FROM_KLAVIYO_PRIVATE_API_KEY = ketl_keys.DECJUBA_FROM_PRIVATE_API_KEY  # 'pk_something'
ketl_client_from = KetlClient(public_api_key=FROM_KLAVIYO_PUBLIC_API_KEY, private_api_key=FROM_KLAVIYO_PRIVATE_API_KEY)
json_data = ketl_client_from.get_metric_timeline_from_klaviyo(metric_id="HA8Rh4", profile_properties_to_save=['$email'], event_properties_to_save=['*'], since=since, until=until)
ketl_client_from.save_json_array_as_csv(json_data)
########################################################################################################################################

# Set timeframe
since = None
until = None

# Get designated metrics and save as json list files
metric_ids = ["LX2awW"]

'''
ketl_client_from.get_and_save_metrics(
        metric_ids,
        profile_properties_to_save=['*'],
        event_properties_to_save=['*'],
        since=None,
        until=None,
        format='retrackable'
    )
'''
'''
email_list = ketl_client_from.get_emails_from_csv(filename="hello_molly_emails", email_column_header="Email")

file_list = ['from - Viewed Product']

file_list = ketl_client_to.filter_retrackable_metric_files(file_list, email_list=email_list)
'''
#ketl_client_to.track_metrics_from_files(file_list, emails=email_list)


############ EXAMPLE ############
# Return a list of JSON of events considered "conversions" from Metric 1 to Metric 2
"""
ORIGIN_METRIC_NAME = 'Clicked Email'  # Name of the metric to consider the start of an engagement (eg. Clicked Email)
ORIGIN_METRIC_ID = 'NDhwfR'  # ID of the metric to consider the start of an engagement
ORIGIN_METRIC_FILTER = {  # Filter for the origin metric (only consider matching events when determining "origins")
        'key': ['properties', '$message'],
        'operator': 'equals',
        'value': 'XQVbjA'
    }
GOAL_METRIC_NAME = 'Ordered Product'  # Name of the metric to consider the conversion action (eg. Ordered Product)
GOAL_METRIC_ID = 'QTZp3R'  # ID of the metric to consider the conversion action
GOAL_METRIC_FILTER = {  # Filter for the goal metric (only consider matching events when determining "conversions")
        'key': ['properties', 'Categories'],
        'operator': 'contains',
        'value': 'KissMe'
    }
JOIN_KEY = '$email'  # Key to determine relationships between
CONVERSION_WINDOW = 5  # Conversion window in days

# grab the metrics
'''
origin_metric_data = ketl.get_metric_timeline_from_klaviyo(
        metric_id=ORIGIN_METRIC_ID,
        profile_properties_to_save=profile_properties_to_save,
        event_properties_to_save=event_properties_to_save,
        since=since, until=until
    )
ketl.save_json_array(origin_metric_data, filename=ORIGIN_METRIC_NAME)

goal_metric_data = ketl.get_metric_timeline_from_klaviyo(
        metric_id=GOAL_METRIC_ID,
        profile_properties_to_save=profile_properties_to_save,
        event_properties_to_save=event_properties_to_save,
        since=since, until=until
    )
ketl.save_json_array(goal_metric_data, filename=GOAL_METRIC_NAME)
'''

# determine which are "conversions"
'''

conversions = ketl.get_conversion_events(origin_events=origin_metric_data,goal_events=goal_metric_data,join_key=JOIN_KEY,goal_events_filter=GOAL_METRIC_FILTER,origin_events_filter=ORIGIN_METRIC_FILTER,window=CONVERSION_WINDOW)
ketl.save_json_array(conversions, filename='Conversions')
ketl.save_json_array_as_csv(conversions,filename='Conversions')



'''
"""
############ EXAMPLE ############
# Assemble an Ordered Product CSV into a Placed Order json array
'''
importlib.reload(ketl)
importlib.reload(ketl_keys)
filepath = './'
filename = 'rrp-import-all'
ordered_products = ketl.load_csv_as_json_array(filepath, filename, unique_id_column_header='$event_id')

join_id = 'Statistic ID'
include_keys = ['*']
exclude_keys = ["Person//First Name",
                "Person//Last Name",
                "Person//Email",
                "Person//Organization",
                "Person//Phone",
                "Person//City",
                "Person//Region",
                "Person//Zip",
                "Person//Country",
                "Statistic ID",
                "Timestamp",
                "Product ID",
                "$event_id",
                "Name",
                "$value",
                "Total",
                "$event_id"]
placed_orders = ketl.placed_order_from_ordered_product(ordered_products, join_id=join_id,
                                                         include_keys=include_keys, exclude_keys=exclude_keys)

placed_order_list = ketl.convert_keyed_json_to_json_list(placed_orders)
ketl.send_klaviyo_track_bulk(json_list=placed_order_list, api_key=ketl_keys.Red_River_Paper_PUBLIC_API_KEY)
'''

############ EXAMPLE ############
# Pull "Placed Order" metric and specific profile properties from Thrive Causemetics
"""
METRIC_ID = 'HeLlOo'
# since_datetime = '2020-05-07 00:00:00' # datetime string
# until_datetime = '2020-05-14 00:00:00' # datetime string
# since = datetime.timestamp(datetime.strptime(since_datetime, '%Y-%m-%d %H:%M:%S')) # unix timestamp for lower bound
# until = datetime.timestamp(datetime.strptime(until_datetime, '%Y-%m-%d %H:%M:%S')) # unix timestamp for upper bound

# Retrack Engagement Data to different account
from_pkey = 'pk_a7def455a3c048feed41c81628fe3d3e60'
KLAVIYO_PRIVATE_API_KEY = from_pkey

from_Opened_Email = 'Hs64UT'
from_Received_Email = 'NPmHsk'
from_Bounced_Email = 'Ps4tjx'
from_Clicked_Email = 'HwHjgh'

to_key = 'NNk6pK'
KLAVIYO_PUBLIC_API_KEY = to_key
since = None
until = None
'''
json_data = get_metric_timeline_from_klaviyo(metric_id=from_Opened_Email, profile_properties_to_save=profile_properties_to_save, event_properties_to_save=event_properties_to_save, since=since, until=until)
save_json_array(json_data, filename='from_Opened_Email')

json_data2 = get_metric_timeline_from_klaviyo(metric_id=from_Received_Email, profile_properties_to_save=profile_properties_to_save, event_properties_to_save=event_properties_to_save, since=since, until=until)
save_json_array(json_data2, filename='from_Received_Email')

json_data3 = get_metric_timeline_from_klaviyo(metric_id=from_Bounced_Email, profile_properties_to_save=profile_properties_to_save, event_properties_to_save=event_properties_to_save, since=since, until=until)
save_json_array(json_data3, filename='from_Bounced_Email')

json_data4 = get_metric_timeline_from_klaviyo(metric_id=from_Clicked_Email, profile_properties_to_save=profile_properties_to_save, event_properties_to_save=event_properties_to_save, since=since, until=until)
save_json_array(json_data4, filename='from_Clicked_Email')
'''
''''''
# retrack for everyone
file_list = ['from_Opened_Email', 'from_Received_Email', 'from_Bounced_Email', 'from_Clicked_Email']
file_list = ['from_Received_Email']  # 82500 for rec em
file_list = ['from_Bounced_Email', 'from_Clicked_Email']
# file_list = ['from_Bounced_Email']
for json_file in file_list:
    json_list = load_json_array('./', json_file)
    send_klaviyo_track_bulk(json_list=json_list, api_key=KLAVIYO_PUBLIC_API_KEY)

response = ''
for json_file in file_list:
    json_list = load_json_array('./', json_file)
    response = send_klaviyo_track(json_list[0], api_key=KLAVIYO_PUBLIC_API_KEY)

''''''
'''
# only retrack for certain emails
json_list = load_json_array('./', 'thrive_data')
retrack = []
for item in json_list:
    for email in emails:
        if email == item.get('customer_properties').get('email'):
            retrack.append(item)
            break
save_json_array(retrack, filename='thrive_data_retrack')
print(retrack[0])
json_list = load_json_array('./', 'thrive_data_retrack')
send_klaviyo_track_bulk(json_list=json_list,api_key=KLAVIYO_PUBLIC_API_KEY)
'''
"""

############ EXAMPLE ############
# Pull "Submitted NPS Form" metric and specific profile properties from Klaviyo
'''
METRIC_ID = 'LK8TYz'
since = None
until = None
profile_properties_to_save = ['email', 'K4KBecameCustomerDate', 'K4KCustomerSegment', 'K4KManagedBy', 'K4KMRR', 'K4KOBS', 'K4KSalesStatus', 'ActiveEcommerceIntegration']
json_data = get_metric_timeline_from_klaviyo(metric_id=METRIC_ID, profile_properties_to_save=profile_properties_to_save, event_properties_to_save=event_properties_to_save, since=since, until=until)
#save_json_array(json_data, filename='Submitted NPS Form')
#json_data = load_json_array('./', 'Submitted NPS Form')
save_json_array_as_csv(json_data,filename='Submitted NPS Form')
'''

############ EXAMPLE ############
# Pull Suppressions
'''
json_data = get_suppressions_from_klaviyo(page_size=1000,since=since,until=until)
#json_data = load_json_array('./', 'data_export_original')
save_json_array(json_data,filename='Suppressions')
save_json_array_as_csv(json_data,filename='Suppressions')
'''

############ EXAMPLE ############
# JSON 2 CSV
'''
json_data = load_json_array('./', 'test')
save_json_array_as_csv(json_data,filename='test')
'''
