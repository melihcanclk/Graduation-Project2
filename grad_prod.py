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

CSV_WRITE_NAME = "data" + date + ".csv"

iterator = pd.read_csv(
    "PP_GUNICIISLEM.M." + date + ".csv",
    chunksize=CHUNK_SIZE,
    sep=";",
    dtype=str,
    low_memory=False,
)

data = pd.DataFrame({
    "ISLEM ZAMANI": [],
    "HACIM": [],
})

pd.set_option("display.float_format", "{:.2f}".format)

# write ISLEM ZAMANI and HACIM  colnames to csv file
data.to_csv(CSV_WRITE_NAME, mode="a", header=True, index=False, sep=";")

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
            "ISLEM ZAMANI": [],
            "HACIM": [],
        })
        temp_data["ISLEM ZAMANI"] = chunk[chunk["ISLEM ZAMANI"].notna()]["ISLEM ZAMANI"]
        temp_data["ISLEM ZAMANI"] = temp_data["ISLEM ZAMANI"].dt.time

        # filter if date is not NaT

        chunk["ISLEM HACMI"] = pd.to_numeric(chunk["ISLEM HACMI"], errors="coerce")
        temp_data["HACIM"] = chunk[chunk["ISLEM HACMI"].notna()]["ISLEM HACMI"]

        # append temp_data to data

        data = pd.concat([data, temp_data], ignore_index=True)

        # write temp_data to same csv file by appending
        temp_data.to_csv(CSV_WRITE_NAME, mode="a", header=False, index=False, sep=";")

        print("Chunk " + str(i) + " is done")

        i += 1
    else:
        break


