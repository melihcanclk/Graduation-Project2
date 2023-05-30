import os
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from constants import *

pd.set_option("display.float_format", "{:.2f}".format)

data = pd.DataFrame(
    {
        "TARIH": [],
        "HACIM": [],
    }
)

for chunk in pd.read_csv(
    CSV_WRITE_NAME, sep=";", low_memory=False, chunksize=CHUNK_SIZE
):
    # remove first row
    chunk = chunk.iloc[1:]

    # concat TARIH and ISLEM ZAMANI columns
    chunk["TARIH"] = chunk["TARIH"] + " " + chunk["ISLEM ZAMANI"]

    # remove ISLEM ZAMANI column
    chunk = chunk.drop(columns=["ISLEM ZAMANI"])

    # convert TARIH column to datetime format
    chunk["TARIH"] = pd.to_datetime(chunk["TARIH"], format="%Y-%m-%d %H:%M:%S")

    # convert to date format
    day = pd.to_datetime(day, format="%Y-%m-%d")

    # filter data by date
    chunk = chunk[
        (chunk["TARIH"] >= day) & (chunk["TARIH"] < day + pd.Timedelta(days=1))
    ]

    # sum HACIM column by date and time
    chunk = chunk.groupby(["TARIH"])["HACIM"].sum().reset_index()

    # append chunk to data
    data = pd.concat([data, chunk], ignore_index=True)


data = data.groupby(["TARIH"])["HACIM"].sum().reset_index()


print(data)


# plot data with matplotlib x axis format as date and time, y axis format as float
fig, ax = plt.subplots()
ax.plot(data["TARIH"], data["HACIM"])
# set x axis label
ax.set_xlabel("Date and Time")
# set y axis label
ax.set_ylabel("Volume(₺)")

# set x axis ticks as every minute
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))

# format date and time
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))

ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
plt.gcf().autofmt_xdate()  # Rotate and align the tick labels

# save png with date and time
#create folder if not exists
if not os.path.exists("plots"):
    os.makedirs("plots")

plt.savefig("plots/" + day.strftime("%Y-%m-%d") + ".png", dpi=300)

plt.show()
