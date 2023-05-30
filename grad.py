import pandas as pd
import matplotlib.pyplot as plt
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
)

for chunk in iterator:
    # print each chunk row by row
    chunk = chunk.loc[:, colnames]
    # print_chunks_by_row(chunk)
    # plot each chunk
    data = pd.DataFrame()

    chunk["ISLEM ZAMANI"] = pd.to_datetime(chunk["ISLEM ZAMANI"], format="%H:%M:%S.%f", errors="coerce")
    data["DATE"] = chunk["ISLEM ZAMANI"]
    #filter if date is not NaT
    data = data[data["DATE"].notna()]
    data["DATE"] = data["DATE"].dt.time
    print(data["DATE"]) 


    chunk["ISLEM FIYATI"] = pd.to_numeric(chunk["ISLEM FIYATI"], errors="coerce")
    data["ISLEM FIYATI"] = chunk["ISLEM FIYATI"]
    #if ISLEM FIYATI is not NaN
    data = data[data["ISLEM FIYATI"].notna()]
    print(data["ISLEM FIYATI"])

    #plot data
    data["ISLEM FIYATI"] = data["ISLEM FIYATI"].astype(float)
    data["DATE"] = data["DATE"].astype(str)
    plt.plot(data["DATE"], data["ISLEM FIYATI"])
    plt.show()
    break
