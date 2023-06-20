from os import path, makedirs, system
from tkinter import Tk, Button, Text, Label, messagebox 
from tkinter.filedialog import askopenfilename

from tkinter.ttk import Progressbar

import pandas as pd

from constants import CHUNK_SIZE, holidays

import threading

import calendar

window = Tk()
close_window = False
window.title("Graduation Project Prod UI")
window.geometry("500x250")

def on_closing(thread):
    # ask user if he wants to close the window using messagebox
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        global close_window
        global window
        close_window = True
        window.destroy()
    
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


def askfile(progressed_percent, button):
    filename = (
        askopenfilename()
    )  # show an "Open" dialog box and return the path to the selected file
    if not filename:
        print("No file selected")
        return

    print(filename)

    if not filename.split("/")[-1].startswith("PP_GUNICIISLEM.M.") or not filename.split("/")[-1].endswith(".csv"):
        print("Invalid file name, please select a file with name PP_GUNICIISLEM.M.{year}{month}.csv")
        return
    
    year_month = filename.split("/")[-1].split(".")[2][0:6]
    year = year_month[0:4]
    month = year_month[4:]

    DIRECTORY = "data" + year + month

    if path.exists(DIRECTORY):
        # ask user if he wants to overwrite existing data
        overwrite = messagebox.askyesno(
            "Overwrite", "Directory " + DIRECTORY + " already exists. Do you want to overwrite existing data?"
        )

        if overwrite:
            # delete directory and create again
            system("rm -rf " + DIRECTORY)
            makedirs(DIRECTORY)
        else:
            # exit program
            return
        
    else:
        makedirs(DIRECTORY)

    
    button.config(text="Processing...", state="disabled")

    # get all dates in month
    dates = get_weekdays(int(year), int(month))
    dates = [date for date in dates if date not in holidays]

    for _date in dates:
        _date = _date.strftime("%Y-%m-%d")
        # create csv file with name _date inside DIRECTORY if it doesnt exist
        name = DIRECTORY + "/" + _date + ".csv"
        if not path.isfile(name):
            open(name, "w").close()


    pd.set_option("display.float_format", "{:.2f}".format)

    i = 0

    # get total file size
    total_file_size = path.getsize(filename)
    print(total_file_size)
    print(CHUNK_SIZE)
    progressed_size = 0
    progress_bar["value"] = "0"

    # Start the Tkinter event loop
    window.update()

    stop_flag = threading.Event()

    def process_file():
        nonlocal progressed_size
        nonlocal i
        for chunk in pd.read_csv(
            filename,
            chunksize=CHUNK_SIZE,
            sep=";",
            low_memory=False,
        ):
            if close_window:
                break

            # progress_bar value between 0 and 100
            progressed_size += CHUNK_SIZE
            percentage = progressed_size / total_file_size * 100 * 100
            progressed_percent.config(state="normal")
            progressed_percent.delete(1.0, "end")
            progressed_percent.insert(1.0, str(round(percentage, 2)) + "%")
            progressed_percent.config(state="disabled")
            progress_bar["value"] = percentage
            window.update_idletasks()

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
                    i += 1
                else:
                    filtered_data.to_csv(name, sep=";", index=False, mode="a", header=False)



    thread = threading.Thread(target=process_file)
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(thread))

    thread.start()

    while thread.is_alive() and not stop_flag.is_set():
        window.update()

    stop_flag.set() 

    thread.join()

    print("Done")

description_label = Label(window, text="Select a file to process - file name should \n be PP_GUNICIISLEM.M.{year}{month}.csv")

description_label.place(x=115, y=50)


progress_bar = Progressbar(window, orient="horizontal", length=200, mode="determinate")
progress_bar.place(x=150, y=150)

progressed_percent = Text(window, height=1, width=20)
progressed_percent.insert(1.0, "0%")
progressed_percent.config(state="disabled")
progressed_percent.place(x=170, y=175)

file_button = Button(window, text="Select File")
file_button.config(command=lambda: askfile(progressed_percent, file_button))
file_button.place(x=200, y=100)

# set resizable to false
window.resizable(False, False)
window.mainloop()
