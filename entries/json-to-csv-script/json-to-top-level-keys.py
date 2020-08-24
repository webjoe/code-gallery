import json
import csv

jsonFilepath = '../'
jsonFilename = 'test'

#jsonData = json.loads(jsonFilepath + jsonFilename + '.json')
with open(jsonFilepath + jsonFilename + '.json') as json_file:
    jsonData = json.load(json_file)
    # open a file for writing
    csvData = open(jsonFilepath + jsonFilename + '.csv', 'w')
    # create the csv writer object
    csvwriter = csv.writer(csvData)
    count = 0
    for item in jsonData:
      if count == 0:
         header = item.keys()
         csvwriter.writerow(header)
      count += 1
      csvwriter.writerow(item.values())
    csvData.close()
