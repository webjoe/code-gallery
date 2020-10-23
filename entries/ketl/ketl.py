###### KETTLE (KETL)
######
from datetime import datetime
import base64
import csv
import json
import math
import os
import pysftp
import random
import re
import requests
import time
import urllib
import sys


class KetlClient:
    """Klaviyo Extract Transform Load (KETL): a library for getting data in and out of Klaviyo and other systems as
    well as processing of that data."""

    BYTES_IN_GIGABYTES = 1000000000

    def __init__(self, public_api_key=None, private_api_key=None):
        self.KLAVIYO_PUBLIC_API_KEY = public_api_key
        self.KLAVIYO_PRIVATE_API_KEY = private_api_key

    #####################
    # Utility Functions
    #####################
    def flatten_json(self, json_array):
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '.')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '.')
                    i += 1
            else:
                out[name[:-1]] = x

        flatten(json_array)
        return out

    def get_current_unix_time(self):
        return round(time.time())

    def get_specified_properties(self, properties, properties_to_save=['*']):
        # Return the specified properties from supplied JSON
        # Inputs
        #   properties (JSON): original set of properties
        #   properties_to_save (array): list of keys to keep (or ['*'] for all keys)
        # Returns
        #   properties_to_return (JSON): filtered set of properties
        if properties_to_save == ['*']:
            return properties
        properties_to_return = {}
        for key in properties:
            if key in properties_to_save:
                properties_to_return[key] = properties[key]
        return properties_to_return

    def remove_specified_properties(self, properties, properties_to_remove=None):
        # Return the specified properties from supplied JSON
        # Inputs
        #   properties (JSON): original set of properties
        #   properties_to_remove (array): list of keys to remove
        # Returns
        #   properties_to_return (JSON): filtered set of properties
        if properties_to_remove == None:
            return properties
        properties_to_return = {}
        for key in properties:
            if not key in properties_to_remove:
                properties_to_return[key] = properties[key]
        return properties_to_return

    def inside_since_until(self, current, since=None, until=None):
        '''
        Usage: check to see if are still within a provided since or until parameter
        Inputs
            since (unix timestamp): target 'since' parameter to start with
            until (unix timestamp): target 'until' parameter to end with
            current (unix timestamp): the current timestamp being compared
        Returns
            (boolean): true if you are within the provided times, otherwise false
        '''
        if since and current < since:
            return False
        if until and current > until:
            return False
        return True

    def setup_sftp_client(self, host, username=None, private_key=None, password=None, port=22, private_key_pass=None,
                          ciphers=None, log=False):
        return pysftp.Connection(host=host, username=username, private_key=private_key, password=password, port=port,
                                 private_key_pass=private_key_pass, ciphers=ciphers, log=log)

    def access_nested_key(self, obj, keys):
        if isinstance(keys, str):
            return obj.get(keys)
        if len(keys) == 0:
            return obj
        if obj.get(keys[0]):
            return self.access_nested_key(obj[keys[0]], keys[1:len(keys)])

    def event_fits_filter(self, event_data, event_filter=None):
        # If there's no filter, it fits the filter!
        if not event_filter:
            return True
        # If the filter isn't constructed correctly, it doesn't fit the filter
        if not (event_filter.get('key') or event_filter.get('operator') or event_filter.get('value')):
            return False
        if event_filter['operator'] == 'equals':
            if event_filter['value'] == self.access_nested_key(event_data, event_filter['key']):
                return True
        if event_filter['operator'] == 'contains' and event_data:
            if event_filter['value'] in self.access_nested_key(event_data, event_filter['key']):
                return True
        return False

    def get_conversion_events(self, origin_events, goal_events, join_key,
                              origin_events_filter=None, goal_events_filter=None, window=None):
        # Filter origin events.
        filtered_origin_events = []
        join_key_uniques = []
        for origin_event in origin_events:
            if self.event_fits_filter(origin_event, origin_events_filter):
                filtered_origin_events.append(origin_event)
                join_key_uniques.append(origin_event['customer_properties'].get(join_key))
        # Filter goal events.
        filtered_goal_events = []
        window_in_seconds = window * 24 * 60 * 60
        unique_conversions_by_join_key = []
        for goal_event in goal_events:
            if self.event_fits_filter(goal_event, goal_events_filter) and \
                    goal_event['customer_properties'].get(join_key) in join_key_uniques:
                if not window:
                    filtered_goal_events.append(goal_event)
                else:
                    for filtered_origin_event in filtered_origin_events:
                        if filtered_origin_event['customer_properties'].get(join_key) == goal_event[
                            'customer_properties'].get(join_key) and \
                                not goal_event['customer_properties'].get(
                                    join_key) in unique_conversions_by_join_key and \
                                filtered_origin_event['time'] > filtered_origin_event['time'] - window_in_seconds:
                            # Log that we've tracked a conversion already for this person by their unique "join key"
                            unique_conversions_by_join_key.append(goal_event['customer_properties'].get(join_key))
                            filtered_goal_events.append(goal_event)
        return filtered_goal_events

    def convert_raw_event_to_retrackable(self, event_data):
        """Converts event data returned from the Metrics API to a format that can be sent as a Track request to generate an
            identical event. The Metrics API returns data in a format slightly different from what was originally sent.
        Args:
            event_data (dict): The raw event data returned by the API.
        Returns:
            dict: Converted event data.
        """
        converted_data = {
            'event': event_data.get('event_name'),
            'datetime': event_data.get('datetime'),
            'time': event_data.get('timestamp'),
            'customer_properties': event_data.get('person')[0],
            'properties': event_data.get('event_properties')
        }
        if converted_data['customer_properties'].get('email'):
            converted_data['customer_properties']['$email'] = converted_data['customer_properties'].pop('email')
        if converted_data['properties'].get('$extra'):
            converted_data['properties']['extra'] = converted_data['properties'].pop('$extra')
        return converted_data

    def get_filtered_json(self, original_json, include_keys=['*'], exclude_keys=None):
        filtered_json = original_json
        if not include_keys == ['*'] and exclude_keys:
            for key in include_keys:
                if key in exclude_keys:
                    print("get_filtered_json sent conflicting key arguments")
                    return filtered_json
        elif not include_keys == ['*']:
            filtered_json = self.get_specified_properties(filtered_json, properties_to_save=include_keys)
        elif exclude_keys:
            filtered_json = self.remove_specified_properties(filtered_json, properties_to_remove=exclude_keys)
        return filtered_json

    def convert_keyed_json_to_json_list(self, keyed_json):
        json_list = []
        for key in keyed_json:
            json_list.append(keyed_json[key])
        return json_list

    def convert_json_list_keyed_json(self, json_list, id_key):
        keyed_json = {}
        for item in json_list:
            keyed_json[item[id_key]] = item
        return keyed_json

    def placed_order_from_ordered_product(self, ordered_products, join_id, include_keys=None, exclude_keys=None):
        print('Merging "Ordered Product" events...')
        datetime_format = '%m/%d/%Y %H:%M'
        placed_orders = {}
        for key in ordered_products:
            item = ordered_products[key]
            current_id = item[join_id]
            filtered_item = self.get_filtered_json(item, include_keys=include_keys, exclude_keys=exclude_keys)
            if not current_id in placed_orders:  # If this is a new order, set up the new order payload.
                placed_orders[current_id] = {
                    "event": "Placed Order",
                    "customer_properties": {
                        "$email": item["Person//Email"]
                    },
                    "properties": {
                        "$event_id": current_id,
                        # "$value": item["$value"],
                        "$value": float(item["Total"]),
                        "ItemNames": [item["Name"]],
                        "Items": [{
                            "SKU": item["Product ID"],
                            "ProductName": item["Name"],
                            "ItemPrice": float(item["$value"]),
                            "RowTotal": float(item["$value"]) * float(item["Quantity"]),
                            "Quantity": float(item["Quantity"])
                        }]
                    },
                    "time": datetime.timestamp(datetime.strptime(item["Timestamp"], datetime_format))
                }
            else:  # If this is an already logged order, just append the item
                # placed_orders[current_id]["properties"]["$value"] += float(item["$value"])
                placed_orders[current_id]["properties"]["ItemNames"].append(item["Name"])
                placed_orders[current_id]["properties"]["Items"].append({
                    "SKU": item["Product ID"],
                    "ProductName": item["Name"],
                    "ItemPrice": float(item["$value"]),
                    "RowTotal": float(item["$value"]) * float(item["Quantity"]),
                    "Quantity": float(item["Quantity"])
                })
        print('Merging complete!')
        return placed_orders

    def get_filesize_in_mb(self, filename, filepath='./'):
        # get file size in MB
        return os.stat('{filepath}{filename}'.format(filepath=filepath, filename=filename)).st_size / 1000 / 1000

    def get_num_rows_in_file(self, filehandler):
        return sum(1 for line in filehandler)

    def get_rows_per_filesize_in_mb(self, filename, num_rows_in_file, filepath='./', target_filesize_in_mb=45):
        # gets the number of rows needed to hit a file size in MB
        return num_rows_in_file / self.get_filesize_in_mb(filename, filepath=filepath) * target_filesize_in_mb

    # Add a random sample segment tag to each row in a CSV
    def assign_random_sample_segments(self, filename, filepath='./', sample_size=1000):
        fileparts = os.path.splitext(filename)
        filename = fileparts[0]
        file_ext = fileparts[1]

        fid = open(filepath + filename + file_ext, "r")
        csv_lines = fid.readlines()
        fid.close()
        # Grab header before shuffle
        header = 'Sample Segment,' + csv_lines.pop(0)
        # Shuffle rows
        random.shuffle(csv_lines)
        # Loop through lines and add current segment number
        sample_segment = 0
        counter = 0
        for row in range(0, len(csv_lines)):
            csv_lines[row] = str(sample_segment) + ',' + csv_lines[row]
            counter = counter + 1
            if counter == sample_size:
                counter = 0
                sample_segment = sample_segment + 1
        # Save to new file
        fid = open(filepath + filename + '_random_sample_segments' + file_ext, "w")
        fid.writelines([header] + csv_lines)
        fid.close()

    # return the number of rows to split the CSV by given the desired filesize
    def split_csv(self, filename, filepath='./', target_filesize_in_mb=45, delimiter=','):
        print('Calulating file metrics...')
        fileparts = os.path.splitext(filename)
        filename = fileparts[0]
        file_ext = fileparts[1]
        file_size = self.get_filesize_in_mb(filename + file_ext, filepath=filepath)
        with open(filepath + filename + file_ext, 'rb') as csvfileIn:
            num_rows_in_file = self.get_num_rows_in_file(csvfileIn)
        with open(filepath + filename + file_ext, 'rb') as csvfileIn:
            reader = csv.reader(csvfileIn, delimiter=',')
            row_limit = self.get_rows_per_filesize_in_mb(filename + file_ext, filepath=filepath,
                                                         target_filesize_in_mb=target_filesize_in_mb,
                                                         num_rows_in_file=num_rows_in_file)
            num_files = num_rows_in_file / row_limit + 1
            print('| Original File Size: ' + str(file_size) + 'MB | Target File Size: ' + str(
                target_filesize_in_mb) + 'MB | \n' +
                  '| Original File Row Count: ' + str(num_rows_in_file) + ' Rows | Target File Row Count: ' + str(
                        row_limit) + ' Rows | \n' +
                  '| Number of Output Files: ' + str(num_files) + ' |')
            current_part = 1
            writer = csv.writer(open(filepath + filename + '_part' + str(current_part) + file_ext, 'wb'),
                                delimiter=delimiter)
            current_limit = row_limit
            print('Processing file part: ' + str(current_part) + ' out of ' + str(num_files))
            headers = reader.next()
            writer.writerow(headers)
            for i, row in enumerate(reader):
                if i + 1 > current_limit:
                    current_part += 1
                    print('Processing file part: ' + str(current_part) + ' out of ' + str(num_files))
                    current_limit = row_limit * current_part
                    writer = csv.writer(open(filepath + filename + '_part' + str(current_part) + file_ext, 'wb'),
                                        delimiter=delimiter)
                    writer.writerow(headers)
                writer.writerow(row)

    def get_emails_from_csv(self, filename, email_column_header):
        # open the file in universal line ending mode
        with open(f"{filename}.csv", 'rU') as infile:
            # read the file as a dictionary for each row ({header : value})
            reader = csv.DictReader(infile)
            data = {}
            for row in reader:
                for header, value in row.items():
                    try:
                        data[header].append(value)
                    except KeyError:
                        data[header] = [value]
        return data[email_column_header]

    def generate_unique_id(self):
        return f"{str(int(round(time.time() * 1000)))}_{str(random.randrange(999999))}"

    def time_to_save(self, obj, size_threshold=BYTES_IN_GIGABYTES):
        """ Tells you whether or not an object is becoming too big to save
        Args:
            obj (arbitrary json stringifyable type): object to check for potential bigness
            size_threshold (int):
        """
        if sys.getsizeof(json.dumps(obj)) > size_threshold:
            return True
        return False

    #####################
    # KETL Utility Functions
    #####################
    def get_and_save_metrics(
            self,
            metric_ids,
            profile_properties_to_save=['*'],
            event_properties_to_save=['*'],
            since=None,
            until=None,
            format='retrackable'
    ):
        for metric_id in metric_ids:
            self.get_and_save_metric(
                metric_id=metric_id,
                profile_properties_to_save=profile_properties_to_save,
                event_properties_to_save=event_properties_to_save,
                since=since,
                until=until,
                format=format
            )

    def get_and_save_metric(
            self,
            metric_id,
            profile_properties_to_save=['*'],
            event_properties_to_save=['*'],
            since=None,
            until=None,
            format='retrackable'
    ):
        json_data = self.get_metric_timeline_from_klaviyo(
            metric_id=metric_id,
            profile_properties_to_save=profile_properties_to_save,
            event_properties_to_save=event_properties_to_save,
            since=since,
            until=until,
            format=format
        )
        self.save_json_array(json_data, filename=f"from - {metric_id} part last")

    def filter_retrackable_metric_files(self, file_list, email_list=None):
        filtered_metric_files = []
        for filename in file_list:
            filtered_metric_files.append(self.filter_retrackable_metric_file(filename, email_list=email_list))
        return filtered_metric_files

    def filter_retrackable_metric_file(self, filename, email_list=None):
        if not email_list:
            return filename
        print(f"Filtering \"{filename}\"")
        json_list = self.load_json_array('./', filename)
        retrack = []
        for item in json_list:
            for email in email_list:
                if email == item.get('customer_properties').get('email'):
                    print(item)
                    # retrack.append(item)
                    break
        filename = f"metrics_to_retrack_{self.generate_unique_id()}"
        # self.save_json_array(retrack, filename=filename)
        print('Done!')
        return filename

    def track_metrics_from_files(self, metric_files):
        for metric_file in metric_files:
            self.track_metric_from_file(metric_file)

    def track_metric_from_file(self, filename):
        print(f"Tracking \"{filename}\" to Klaviyo")
        json_list = self.load_json_array('./', filename)
        self.send_klaviyo_track_bulk(json_list=json_list)
        print('Done!')

    #####################
    # Read Data - Remote
    #####################
    def get_metric_timeline_from_klaviyo(self, metric_id, profile_properties_to_save=['*'], event_properties_to_save=['*'],
                                         since=None, until=None, format='retrackable'):
        """Converts event data returned from the Metrics API to a format that can be sent as a Track request to generate an
            identical event. The Metrics API returns data in a format slightly different from what was originally sent.
        Args:
            metric_id (str): String ID of the metric to be retrieved.
            profile_properties_to_save (list): List of keys for profile properties to preserve on returned dict.
            event_properties_to_save (list): List of keys for event properties to preserve on returned dict.
            since (float): The lower-bound unix timestamp to sync events within (unix timestamp must be > since).
            until (float): The upper-bound unix timestamp to sync events within (unix timestamp must be < until).
            format (str): Specify the desired return format for the event data. Default: 'retrackable'
        Returns:
            list: List of JSON payloads for each event retrieved.
        """
        retrieved_data = []
        url = 'https://a.klaviyo.com/api/v1/metric/{}/timeline'.format(metric_id)
        if since:
            start = since
            sort = "asc"
        elif until:
            start = until
            sort = "desc"
        else:
            start = self.get_current_unix_time()
            sort = "desc"
        params = {'api_key': self.KLAVIYO_PRIVATE_API_KEY, "since": start, 'sort': sort}
        response = requests.request('GET', url, params=params)
        print(url)
        print(params)
        response_json = response.json()
        counter = 1
        file_num = 1
        while True:
            print('Page ' + str(counter))
            for item in response_json['data']:
                timestamp = item.get('timestamp')
                if not self.inside_since_until(timestamp, until=until, since=since):
                    return retrieved_data
                else:
                    # Filter for only the specified profile and event properties.
                    item['person'] = self.get_specified_properties(item.get('person'), profile_properties_to_save),
                    item['event_properties'] = self.get_specified_properties(item.get('event_properties'),
                                                                        event_properties_to_save)
                    # Optionally convert to a "retrackable" event structure.
                    if format == 'retrackable':
                        item = self.convert_raw_event_to_retrackable(item)
                    retrieved_data.append(item)
                    if self.time_to_save(retrieved_data):
                        print(f"saving file {file_num}")
                        self.save_json_array(retrieved_data, filename=f"from - {metric_id} part {file_num}")
                        file_num += 1
                        retrieved_data = []
            if not response_json.get('next'):
                break
            params['since'] = response_json.get('next')
            counter = counter + 1
            response = requests.request('GET', url, params=params)
            response_json = response.json()
        return retrieved_data

    def get_suppressions_from_klaviyo(self, page_size=500, since=None, until=None):
        filepath = os.getcwd() + '/'
        filename = 'Klaviyo_Export_Suppressions'
        retrieved_data = []
        page_size = 5000 if page_size > 5000 or page_size < 1 else page_size
        url = 'https://a.klaviyo.com/api/v1/people/exclusions'
        params = {'api_key': self.KLAVIYO_PRIVATE_API_KEY, 'count': 1}
        response = requests.request('GET', url, params=params)
        total_suppressions = response.json().get('total', 0)
        total_pages = int(math.ceil(total_suppressions / page_size))
        # Make requests
        for page in range(0, total_pages + 1):
            url = 'https://a.klaviyo.com/api/v1/people/exclusions'
            params = {'api_key': self.KLAVIYO_PRIVATE_API_KEY, 'sort': 'desc', 'count': page_size, 'page': page}
            response = requests.request('GET', url, params=params)
            # Check for errors
            if response.status_code == 200:
                response_data = response.json().get('data', [])
                print('page: ' + str(page) + '/' + str(total_pages) + ' (status code: ' + str(
                    response.status_code) + ')')
                # Save row to file
                for item in response_data:
                    timestamp = datetime.timestamp(datetime.strptime(item.get('timestamp'), '%Y-%m-%d %H:%M:%S'))
                    if not self.inside_since_until(timestamp, since=since):
                        print('Done!')
                        return retrieved_data
                    if self.inside_since_until(timestamp, until=until):
                        item['unix_timestamp'] = int(timestamp)
                        retrieved_data.append(item)
            elif response.status_code == 404:
                print('page: ' + str(page) + '/' + str(total_pages) + ' (status code: ' + str(
                    response.status_code) + ')')
            else:
                print('page: ' + str(page) + '/' + str(total_pages) + ' (status code: ' + str(
                    response.status_code) + ')')
                break
        print('Done!')
        return retrieved_data

    def metrics_api(self):
        return None

    def profiles_api(self):
        return None

    def lists_api(self):
        return None

    def lists_api_v2(self):
        return None

    def campaigns_api(self):
        return None

    def templates_api(self):
        return None

    def flows_api(self):
        return None

    def custom_objects_api(self):
        return None

    def get_file_from_sftp(self, sftp_client, sftp_filename, local_directory=os.getcwd() + '/', local_filename=None,
                           sftp_directory='./'):
        local_filename = local_filename if local_filename else sftp_filename
        sftp_client.get(remotepath=sftp_directory + sftp_filename, localpath=local_directory + local_filename)

    #####################
    # Read Data - Local
    #####################
    def load_json_array(self, filepath, filename):
        print('Loading "' + str(filename) + '"...')
        with open(filepath + filename + '.txt') as json_file:
            json_data = json.load(json_file)
        print('"' + str(filename) + '" loaded!')
        return json_data

    def load_csv_as_json_array(self, filepath, filename, unique_id_column_header):
        print('Loading "' + str(filename) + '"...')
        json_data = {}
        with open(filepath + filename + '.csv', errors='ignore') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                json_data[row[unique_id_column_header]] = dict(row)
        print('"' + str(filename) + '" loaded!')
        return json_data

    #####################
    # Write Data - Remote
    #####################
    def send_klaviyo_track_bulk(self, json_list):
        if not self.KLAVIYO_PUBLIC_API_KEY:
            print("No public API key set")
            return
        counter = 0
        total = len(json_list)
        failed_tracks = []
        print('Starting track batch')
        for item in json_list:
            item.pop('datetime', None)
            # item.pop('time')
            # item['properties'].pop('$event_id')
            # item['event'] = item.get('event') + ' Catchup'
            counter = counter + 1
            if counter % 50 == 0:
                print('Sending ' + str(counter) + ' out of ' + str(total) + ' Track requests')
            response = self.send_klaviyo_track(json_payload=item)
            if response.text == '0':
                failed_tracks.append(item)
        print('Done!')
        if len(failed_tracks):
            print('Saving failed Track requests as ' + str(json_list[0].get('event')) + ' failed Tracks.txt')
            self.save_json_array(failed_tracks, filename=str(json_list[0].get('event')) + ' failed Tracks')
        return failed_tracks

    def send_klaviyo_track(self, json_payload):
        if not json_payload.get('token'):
            if not self.KLAVIYO_PUBLIC_API_KEY:
                print("No public API key set")
                return
            json_payload['token'] = self.KLAVIYO_PUBLIC_API_KEY
        url = 'https://a.klaviyo.com/api/track'
        json_str = json.dumps(json_payload).replace('null', '[]').replace('true', '[]').replace('false', '[]')
        # encoded_json_payload = base64.urlsafe_b64encode(json_str.encode()).decode()
        encoded_json_payload = base64.b64encode(bytes(json_str, 'utf-8'))
        # encoded_json_payload = urllib.parse.quote_plus(encoded_json_payload, safe='')
        params = {"data": encoded_json_payload}
        # print(params)
        # requests.request("GET", url, params=params)
        url = url + '?' + urllib.parse.urlencode(params, doseq=True)
        # print(url)
        return requests.request("GET", url)

    def send_file_to_sftp(self, sftp_client, local_filename, local_directory=os.getcwd() + '/', sftp_directory='./',
                          sftp_filename=None):
        sftp_filename = sftp_filename if sftp_filename else local_filename
        sftp_client.put(localpath=local_directory + local_filename, remotepath=sftp_directory + sftp_filename)

    #####################
    # Write Data - Local
    #####################
    def save_json_array(self, json_array, filepath='./', filename='data_export'):
        with open(filepath + filename + '.txt', 'w') as outfile:
            json.dump(json_array, outfile)

    def save_json_array_as_csv(self, json_array, filepath='./', filename='data_export'):
        # Saves an array of JSON as a CSV (one row per item)
        # Inputs
        #   json_array (array of JSON): list of JSON items to save as a CSV
        # Outputs
        #   CSV of one flattened JSON per row with unique keys as column headers
        column_headers = []
        json_array_flattened = []
        record_total = len(json_array)
        counter = 1
        for item in json_array:
            item_flattened = self.flatten_json(item)
            json_array_flattened.append(item_flattened)
            for key in item_flattened:
                if not key in column_headers:
                    column_headers.append(key)
        # save_json_array(json_array_flattened,'flattened')
        with open(filepath + filename + '.csv', 'w') as newFile:
            newFileWriter = csv.writer(newFile)
            newFileWriter.writerow(column_headers)  # add column headers
            for item in json_array_flattened:
                this_row = []
                for col in column_headers:
                    this_row.append(str(item.get(col, '')).encode('utf-8').decode('utf-8'))
                newFileWriter.writerow(this_row)
                if counter % 100 == 0:
                    print('Records Processed: ' + str(counter) + '/' + str(record_total))
                counter = counter + 1
        print('Done!')
