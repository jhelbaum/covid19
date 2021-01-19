#!/usr/bin/env python3

import csv
import datetime
import json

datafile = "scraped/2021_01_18_18_34_56.json"
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

columns = ['Date', 'Cases', 'Recoveries', 'Fatalities', 'Tests', 'Positive', 'Hospitalizations', 'Ventilators', 'Critical', 'Serious', 'Moderate', 'Mild', 'Cumulative serious', 'First dose', 'Second dose']

with open('cases.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=columns, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for date in sorted(entries.keys()):
        writer.writerow(entries[date])
