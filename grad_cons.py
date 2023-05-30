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


# plot data with matplotlib
# Combine date and time columns into a single datetime column
data['DateTime'] = pd.to_datetime(data['TARIH'] + ' ' + data['ISLEM ZAMANI'])

# Plot the data
plt.plot(data['DateTime'], data['ISLEM HACMI'])

# y axis in millions
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
# Format the x-axis as date and time
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.gcf().autofmt_xdate()  # Rotate and align the tick labels

# Set labels and title
plt.xlabel('ISLEM ZAMANI')
plt.ylabel('ISLEM HACMI')
plt.title('Plot of ISLEM HACMI over time')

# save plot as png
plt.savefig(day + '.png')

# Display the plot
plt.show()