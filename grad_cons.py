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
        "ISLEM ZAMANI": [],
        "ISLEM HACMI": [],
    }
)

day = "2023-04-05"

for chunk in pd.read_csv(
    day + CSV_WRITE_NAME, sep=";", low_memory=False, chunksize=CHUNK_SIZE
):

    # append chunk to data
    data = pd.concat([data, chunk], ignore_index=True)
    print("Chunk appended")


# add ISLEM HACMI if ISLEM ZAMANI is the same
data = data.groupby(["TARIH", "ISLEM ZAMANI"])["ISLEM HACMI"].sum().reset_index()

print(data)

# convert ISLEM ZAMANI to datetime
data["ISLEM ZAMANI"] = pd.to_datetime(data["ISLEM ZAMANI"], format="%H:%M:%S")

# plot data
fig, ax = plt.subplots(figsize=(15, 7))

#plot by showing points 
ax.plot(data["ISLEM ZAMANI"], data["ISLEM HACMI"], "o-")
# x axis in minutes 
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
# format x axis
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

#y axis in millions
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: "%dM" % (y * 1e-6)))

ax.set_xlabel("Time(m)")
ax.set_ylabel("Volume(₺)")
# rotate x axis labels
plt.xticks(rotation=90)
ax.set_title("Volume by time")
plt.show()
