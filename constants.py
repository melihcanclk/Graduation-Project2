import pandas as pd
import calendar

def get_weekdays(year, month):
    cal = calendar.Calendar()
    weekdays = []
    
    # Iterate over each day in the specified month
    for day in cal.itermonthdates(year, month):
        # Filter out days that belong to the next or previous month
        if day.month == month:
            # Check if the day is a weekday (0-4 represent Monday-Friday)
            if day.weekday() < 5:
                weekdays.append(day)
    
    return weekdays

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

CHUNK_SIZE = 9000000 # nearly 8 GB data in one chunk moved to RAM 

year = "2023"
month = "01"

DIRECTORY = "data" + year + month

# get all dates in month
dates = get_weekdays(int(year), int(month))

# take holidays out
# holidays are 1 jan, 21, 22, 23 april, 1 may, 19 may, 28 june, 29 june, 30 june, 1 july, 15 july, 30 august, 28 october, 29 october for 2023
holidays = [
    "2023-01-01",
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

dates = [date for date in dates if date not in holidays]