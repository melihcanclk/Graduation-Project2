import os
import pandas as pd
from constants import *
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


year = "2023"
month = "02"

DIRECTORY = "data" + year + month

# get all dates in month
dates = get_weekdays(int(year), int(month))
dates = [date for date in dates if date not in holidays]

# create directory named DIRECTORY if it doesnt exist
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)
else:
    # ask user if he wants to overwrite existing data
    overwrite = input(
        "Directory "
        + DIRECTORY
        + " already exists. Do you want to overwrite existing data? (y/n) "
    )
    overwrite = overwrite.lower()

    if overwrite == "y":
        # delete directory and create again
        os.system("rm -rf " + DIRECTORY)
        os.makedirs(DIRECTORY)
    else:
        # exit program
        exit()


for _date in dates:
    _date = _date.strftime("%Y-%m-%d")
    # create csv file with name _date inside DIRECTORY if it doesnt exist
    name = DIRECTORY + "/" + _date + ".csv"
    if not os.path.isfile(name):
        open(name, "w").close()


pd.set_option("display.float_format", "{:.30f}".format)

i = 0

for chunk in pd.read_csv(
    "PP_GUNICIISLEM.M." + year + month + ".csv",
    chunksize=CHUNK_SIZE,
    sep=";",
    low_memory=False,
):
    # if i != 100:
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
            name = DIRECTORY + "/" + _date + ".csv"
            # write csv with name, if header exists, append to file
            if i == 0:
                filtered_data.to_csv(name, sep=";", index=False)
            else:
                filtered_data.to_csv(name, sep=";", index=False, mode="a", header=False)

        print("Chunk " + str(i) + " processed")

        i += 1
    else:
        break
