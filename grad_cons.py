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
        "ISLEM HACMI": [],
    }
)

for chunk in pd.read_csv(
    CSV_WRITE_NAME, sep=";", low_memory=False, chunksize=CHUNK_SIZE
):

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

    # sum ISLEM HACMI column by date and time
    chunk = chunk.groupby(["TARIH"])["ISLEM HACMI"].sum().reset_index()

    # append chunk to data
    data = pd.concat([data, chunk], ignore_index=True)
    print("Chunk appended")


data = data.groupby(["TARIH"])["ISLEM HACMI"].sum().reset_index()


print(data)


# plot data
fig, ax = plt.subplots(figsize=(15, 7))
ax.plot(data["TARIH"], data["ISLEM HACMI"], color="blue", linewidth=1)
ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_xlabel("Time")
ax.set_ylabel("Volume")
ax.set_title("Volume by time")
plt.show()
