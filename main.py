import json
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib.dates as mdates
from matplotlib.colors import ListedColormap

def main():
    url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=e4bf0ab8-ec88-4f9b-8669-f2cc78273edd&limit=32000'
    fileobj = urllib.request.urlopen(url)

    data = json.loads(fileobj.read())
    records = data['result']['records']

    translations = {
        'date': 'תאריך',
        'hospitalized': 'מאושפזים',
    }

    dates = []
    data = {}
    for record in records:
        for english, hebrew in translations.items():
            if english == 'date':
                dates.append(record[hebrew])
            else:
                data.setdefault(english, []).append(record[hebrew])
    print(data)
    df = pd.DataFrame(data=data, index=pd.Index(dates, 'datetime64[ns]'))
    df['hospitalized'] = df['hospitalized'].astype(int)

    fig, ax = plt.subplots(figsize=(15, 7))
    df.plot.bar(ax=ax)

    # set ticks every week
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # cmap = ListedColormap(['#0343df', '#e50000', '#ffff14', '#929591'])
    # ax = df.plot.bar(x='date', colormap=cmap)
    #
    ax.set_xlabel(None)
    ax.set_ylabel('Hospitalizations')
    ax.set_title('COVID-19 in Israel: Hospitalizations')

    plt.savefig("mygraph.png")

if __name__ == "__main__":
    main()
