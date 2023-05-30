import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from datetime import datetime


def print_chunks_by_row(chunk):
    for index, row in chunk.iterrows():
        print(row)


colnames = [
    "TARIH",
    "ALIS_SATIS",
    "ISLEM ADEDI",
    "ISLEM FIYATI",
    "ISLEM HACMI",
    "ISLEM ZAMANI",
    "SEANS",
    "ISLEM DURUMU",
    "TAKAS TARIHI",
    "AKTIF_PASIF",
    "GUNCELLEME ZAMANI",
    "DEVIR",
    "GUNCELLEME ZAMANI.1",
]


CHUNK_SIZE = 100000
date = "202304"
iterator = pd.read_csv(
    "PP_GUNICIISLEM.M." + date + ".csv",
    chunksize=CHUNK_SIZE,
    sep=";",
    dtype=str,
    low_memory=False,
)

data = pd.DataFrame({
    "TIME": [],
})

pd.set_option("display.float_format", "{:.2f}".format)

# iterate 3 times

i = 0

for chunk in iterator:
    if i != 100:
        # print each chunk row by row
        chunk = chunk.loc[:, colnames]
        # print_chunks_by_row(chunk)
        # plot each chunk
        # print_chunks_by_row(chunk)

        chunk["ISLEM ZAMANI"] = pd.to_datetime(
            chunk["ISLEM ZAMANI"], format="%H:%M:%S.%f", errors="coerce"
        )
        temp_data = pd.DataFrame({
            "TIME": [],
            "HACIM": [],
        })
        temp_data["TIME"] = chunk[chunk["ISLEM ZAMANI"].notna()]["ISLEM ZAMANI"]
        temp_data["TIME"] = temp_data["TIME"].dt.time

        # filter if date is not NaT

        chunk["ISLEM HACMI"] = pd.to_numeric(chunk["ISLEM HACMI"], errors="coerce")
        temp_data["HACIM"] = chunk[chunk["ISLEM HACMI"].notna()]["ISLEM HACMI"]

        # append temp_data to data

        data = pd.concat([data, temp_data], ignore_index=True)

        print("Chunk " + str(i) + " is done")

        i += 1
    else:
        break



# remove seconds from data["TIME"]
data["TIME"] = data["TIME"].apply(lambda x: x.replace(second=0, microsecond=0))

# sum data by minutes
data = data.groupby("TIME").sum()

# convert data["DATE"] to str to plot
data.index = data.index.astype(str)

# plot data
plt.plot(data.index, data["HACIM"])
plt.xlabel("Time")

# set y axis to millions
plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
plt.ylabel("Volume(₺)")
plt.title("Volume by Time")
plt.show()