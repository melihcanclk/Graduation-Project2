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




iterator = pd.read_csv(
    "PP_GUNICIISLEM.M." + month + ".csv",
    chunksize=CHUNK_SIZE,
    sep=";",
    dtype=str,
    low_memory=False,
)

data = pd.DataFrame(
    {
        "TARIH": [],
        "ISLEM ZAMANI": [],
        "HACIM": [],
    }
)

pd.set_option("display.float_format", "{:.2f}".format)

# write ISLEM ZAMANI and HACIM  colnames to csv file if not exists
if not os.path.isfile(CSV_WRITE_NAME):
    data.to_csv(CSV_WRITE_NAME, mode="a", header=True, index=False, sep=";")
    print("File created")
else:
    print("File exists")
    sys.exit()


i = 0

for chunk in iterator:
    if i != 500:
        print("Chunk: ", i)
        chunk["ISLEM ZAMANI"] = pd.to_datetime(
            chunk["ISLEM ZAMANI"], format="%H:%M:%S.%f", errors="coerce"
        )
        # remove first row
        chunk = chunk.iloc[1:]

        temp_data = pd.DataFrame(
            {
                "TARIH": [],
                "ISLEM ZAMANI": [],
                "HACIM": [],
            }
        )

        # save only time, not date
        chunk["ISLEM ZAMANI"] = chunk["ISLEM ZAMANI"].dt.time
        # remove milliseconds
        chunk["ISLEM ZAMANI"] = chunk["ISLEM ZAMANI"].apply(
            lambda x: x.replace(microsecond=0)
        )

        chunk["ISLEM HACMI"] = pd.to_numeric(chunk["ISLEM HACMI"], errors="coerce")

        temp_data["HACIM"] = chunk["ISLEM HACMI"]
        temp_data["TARIH"] = chunk["TARIH"]
        temp_data["ISLEM ZAMANI"] = chunk["ISLEM ZAMANI"]

        # append temp_data to data

        # write temp_data to same csv file by appending
        temp_data.to_csv(CSV_WRITE_NAME, mode="a", header=False, index=False, sep=";")

        i += 1
    else:
        break


