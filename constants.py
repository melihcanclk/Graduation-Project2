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

CHUNK_SIZE = 90000 # nearly 8 GB data in one chunk moved to RAM 

# take holidays out
# holidays are 1 jan, 21, 22, 23 april, 1 may, 19 may, 28 june, 29 june, 30 june, 1 july, 15 july, 30 august, 28 october, 29 october for 2023
holidays = [
    "2023-01-01",
    "2023-02-08",
    "2023-02-09",
    "2023-02-10",
    "2023-02-11",
    "2023-02-12",
    "2023-02-13",
    "2023-02-14",
    "2023-04-21",
    "2023-04-22",
    "2023-04-23",
    "2023-05-01",
    "2023-05-19",
    "2023-06-28",
    "2023-06-29",
    "2023-06-30",
    "2023-07-01",
    "2023-07-15",
    "2023-08-30",
    "2023-10-28",
    "2023-10-29",

]

holidays = [pd.to_datetime(holiday).date() for holiday in holidays]
