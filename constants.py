import pandas as pd

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

CHUNK_SIZE = 10000000

month = "202304"


CSV_WRITE_NAME = "data" + month + ".csv"

dates = pd.date_range(start="2023-04-01", end="2023-04-30", freq="D")