import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from datetime import datetime
from constants import *


def print_chunks_by_row(chunk):
    for index, row in chunk.iterrows():
        print(row)


# if csv file with name = _date + CSV_WRITE_NAME exists, delete it
for _date in dates:
    _date = _date.strftime("%Y-%m-%d")
    name = _date + CSV_WRITE_NAME
    if os.path.isfile(name):
        os.remove(name)
        print("File ", name, " deleted")

pd.set_option("display.float_format", "{:.2f}".format)

i = 0

for chunk in pd.read_csv(
    "PP_GUNICIISLEM.M." + month + ".csv",
    chunksize=CHUNK_SIZE,
    sep=";",
    low_memory=False,
):
    # if i != 1000:
    if 1:
        temp_data = pd.DataFrame(
            {
                "TARIH": [],
                "ISLEM ZAMANI": [],
                "ISLEM HACMI": [],
            }
        )

        chunk["ISLEM ZAMANI"] = pd.to_datetime(
            chunk["ISLEM ZAMANI"], format="%H:%M:%S.%f", errors="coerce"
        )
        # save only time, not date
        chunk["ISLEM ZAMANI"] = chunk["ISLEM ZAMANI"].dt.time
        # remove milliseconds
        chunk["ISLEM ZAMANI"] = chunk["ISLEM ZAMANI"].apply(
            lambda x: x.replace(microsecond=0)
        )

        chunk["ISLEM HACMI"] = pd.to_numeric(chunk["ISLEM HACMI"], errors="coerce")

        temp_data["ISLEM HACMI"] = chunk["ISLEM HACMI"]
        temp_data["TARIH"] = chunk["TARIH"]
        temp_data["ISLEM ZAMANI"] = chunk["ISLEM ZAMANI"]
        for _date in dates:
            _date = _date.strftime("%Y-%m-%d")
            # filter data by date
            filtered_data = temp_data[temp_data["TARIH"] == _date]
            # sum ISLEM HACMI column by date and time
            filtered_data = (
                filtered_data.groupby(["TARIH", "ISLEM ZAMANI"])["ISLEM HACMI"]
                .sum()
                .reset_index()
            )
            # write to csv file
            name = _date + CSV_WRITE_NAME
            # write csv with name, if header exists, append to file
            if os.path.isfile(name):
                filtered_data.to_csv(name, mode="a", index=False, header=False, sep=";")
            else:
                filtered_data.to_csv(name, index=False, header=True, sep=";")

            print("Chunk : ", i, " written to ", name)

        i += 1
    else:
        break
