#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import urllib.request

default_url = 'https://datadashboardapi.health.gov.il/api/queries/_batch'

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--outdir", help="directory with scraped json data files", default="scraped/")
parser.add_argument("-l", "--last_update_filename", help="filename to store last update time", default='last_update.txt')
parser.add_argument("-u", "--url", help="URL for HTTP queries", default=default_url)
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

outdir = args.outdir
url = args.url
last_update_filename = args.last_update_filename
last_update_pathname = outdir + last_update_filename

def fetch_data(requests):
    headers = {
        'Content-Type': 'application/json',
    }
    data = json.dumps(requests)
    data = data.encode('ascii')  # data should be bytes
    req = urllib.request.Request(url, data, headers)
    with urllib.request.urlopen(req) as response:
        data = json.load(response)
    reformatted_data = {}
    for request, item in zip(requests["requests"], data):
        reformatted_data[request["queryName"]] = item["data"]
    return reformatted_data

def check_for_new_update():
    with open(last_update_pathname) as last_update_file:
        recorded_last_update = last_update_file.readline().rstrip()
    print('Last saved update:', recorded_last_update)

    recorded_last_update = datetime.datetime.strptime(recorded_last_update, "%Y_%m_%d_%H_%M_%S")
    last_update_request = {"requests": [{"id": "0", "queryName": "lastUpdate", "single": True, "parameters": {}}]}
    last_update_data = fetch_data(last_update_request)
    last_update = last_update_data["lastUpdate"]["lastUpdate"]
    last_update = datetime.datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S.%fZ').replace(microsecond=0)
    last_update_text = last_update.strftime("%Y_%m_%d_%H_%M_%S")
    if last_update == recorded_last_update:
        print('Already scraped this update, exiting.')
        exit(0)
    return last_update_text

requests = {"requests": [{"id": "0", "queryName": "lastUpdate", "single": True, "parameters": {}},
                         {"id": "1", "queryName": "infectedPerDate", "single": False, "parameters": {}},
                         {"id": "2", "queryName": "updatedPatientsOverallStatus", "single": False, "parameters": {}},
                         {"id": "3", "queryName": "sickPerDateTwoDays", "single": False, "parameters": {}},
                         {"id": "4", "queryName": "sickPatientPerLocation", "single": False, "parameters": {}},
                         {"id": "5", "queryName": "patientsStatus", "single": False, "parameters": {}},
                         {"id": "7", "queryName": "patientsPerDate", "single": False, "parameters": {}},
                         {"id": "8", "queryName": "vaccinated", "single": False, "parameters": {}},
                         {"id": "9", "queryName": "deadPatientsPerDate", "single": False, "parameters": {}},
                         {"id": "10", "queryName": "testResultsPerDate", "single": False, "parameters": {}},
                         {"id": "11", "queryName": "vaccinationsPerAge", "single": False, "parameters": {}},
                         {"id": "13", "queryName": "doublingRate", "single": False, "parameters": {}},
                         {"id": "16", "queryName": "testsPerDate", "single": False, "parameters": {}},
                         {"id": "21", "queryName": "cumSeriusAndBreath", "single": False, "parameters": {}},
                         {"id": "22", "queryName": "averageInfectedPerWeek", "single": False, "parameters": {}},
                         {"id": "26", "queryName": "spotlightLastupdate", "single": False, "parameters": {}},
                         {"id": "27", "queryName": "spotlightAggregatedPublic", "single": True, "parameters": {}},
                         {"id": "30", "queryName": "LastWeekLabResults", "single": False, "parameters": {}},
                         {"id": "31", "queryName": "contagionDataPerCityPublic", "single": False, "parameters": {}},
                         {"id": "34", "queryName": "HospitalBedStatusSegmentation", "single": False, "parameters": {}},
                         {"id": "35", "queryName": "infectedByAgeAndGenderPublic", "single": False,
                        "parameters": {"ageSections": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]}},
                         {"id": "36", "queryName": "isolatedVerifiedDoctorsAndNurses", "single": False, "parameters": {}},
                         {"id": "37", "queryName": "hospitalStatus", "single": False, "parameters": {}},
                         {"id": "44", "queryName": "CalculatedVerified", "single": False, "parameters": {}},
                         {"id": "45", "queryName": "spotlightPublic", "single": False, "parameters": {}}]}

last_update_text = check_for_new_update()

data = fetch_data(requests)

scraped_pathname = os.path.join(outdir, last_update_text + '.json')
with open(scraped_pathname, 'w') as scraped:
    scraped.write(json.dumps(data, indent=2))
print('Wrote data to ' + scraped_pathname)

with open(last_update_pathname, 'w') as last_update_file:
    last_update_file.write(last_update_text)
print('Updated ' + last_update_pathname)
