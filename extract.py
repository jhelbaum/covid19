#!/usr/bin/env python3

import argparse
import csv
import datetime
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--infile", help="input file with scraped json data")
parser.add_argument("-d", "--indir", help="directory with scraped json data files")
parser.add_argument("-l", "--last_update_filename", help="filename to store last update time", default='last_update.txt')
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

last_update_filename = args.last_update_filename
last_update_pathname = os.path.join(args.indir, last_update_filename)

with open(last_update_pathname) as last_update_file:
    recorded_last_update = last_update_file.readline().rstrip()
print('Last saved update: ' + recorded_last_update)

datafile = args.infile
if datafile is None and args.indir is not None:
    datafile = os.path.join(args.indir, recorded_last_update + '.json')
    # datafile = os.path.join(args.indir,sorted(os.listdir(args.indir))[-1])
if datafile is None:
    print("Need either -i or -d!")
    exit(-1)


with open(datafile) as json_file:
    data = json.load(json_file)

# My dataset starts from Feb. 29, 2020.
start_date = datetime.datetime(2020, 2, 29)

cases_by_date = data["infectedPerDate"]
deaths_by_date = data["deadPatientsPerDate"]
tests_by_date = data["testResultsPerDate"]
patients_by_date = data["patientsPerDate"]
vaccinated_by_date = data["vaccinated"]

entries = {}
cases, recoveries = 0, 0


def date_string(date):
    return date.strftime("%Y-%m-%d")


for entry in cases_by_date:
    date = datetime.datetime.strptime(entry["date"], '%Y-%m-%dT%H:%M:%S.%fZ')
    cases += entry["amount"]
    recoveries += entry["recovered"]
    if date < start_date:
        continue
    entries[date_string(date)] = {'Date': date_string(date), 'Cases': cases, 'Recoveries': recoveries, 'Fatalities': 0, 'Tests': 0, 'Positive': 0}

for entry in deaths_by_date:
    date = datetime.datetime.strptime(entry["date"], '%Y-%m-%dT%H:%M:%S.%fZ')
    if date < start_date:
        continue
    entries[date_string(date)]['Fatalities'] = entry["total"]

for entry in patients_by_date:
    date = datetime.datetime.strptime(entry["date"], '%Y-%m-%dT%H:%M:%S.%fZ')
    if date < start_date:
        continue
    entries[date_string(date)]['Hospitalizations'] = entry["Counthospitalized"]
    entries[date_string(date)]['Ventilators'] = entry["CountBreath"]
    entries[date_string(date)]['Critical'] = entry["CountCriticalStatus"]
    entries[date_string(date)]['Serious'] = entry["CountHardStatus"]
    entries[date_string(date)]['Serious but not ventilated'] = entry["CountHardStatus"] - entry["CountBreath"]
    entries[date_string(date)]['Moderate'] = entry["CountMediumStatus"]
    entries[date_string(date)]['Mild'] = entry["CountEasyStatus"]
    entries[date_string(date)]['Cumulative serious'] = entry["CountSeriousCriticalCum"]

tests, positive = 0, 0
for entry in tests_by_date:
    date = datetime.datetime.strptime(entry["date"], '%Y-%m-%dT%H:%M:%S.%fZ')
    tests += entry["amountVirusDiagnosis"]
    positive += entry["positiveAmount"]
    if date < start_date:
        continue
    entries[date_string(date)]['Tests'] = tests
    entries[date_string(date)]['Positive'] = positive

for entry in vaccinated_by_date:
    date = datetime.datetime.strptime(entry["Day_Date"], '%Y-%m-%dT%H:%M:%S.%fZ')
    entries[date_string(date)]['First dose'] = entry['vaccinated']
    entries[date_string(date)]['Second dose'] = entry['vaccinated_seconde_dose']

columns = ['Date', 'Cases', 'Fatalities', 'Recoveries', 'Tests', 'Positive', 'Hospitalizations', 'Ventilators', 'Critical', 'Serious', 'Serious but not ventilated', 'Moderate', 'Mild', 'Cumulative serious', 'First dose', 'Second dose']

with open('cases.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=columns, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for date in sorted(entries.keys()):
        writer.writerow(entries[date])
