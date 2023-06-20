from os import path, makedirs, system
import signal
from tkinter import HORIZONTAL, Scale, Tk, Button, Text, Label, messagebox
from tkinter.filedialog import askopenfilename

from tkinter.ttk import Progressbar

import pandas as pd

from constants import CHUNK_SIZE, holidays

import threading

import calendar

GB = 1000000

filename, DIRECTORY, year, month, chunk_size = None, None, None, None, None

window = Tk()
close_window = False
window.title("Graduation Project Prod UI")
window.geometry("500x400")

def signal_handler(sig, frame):
    global close_window
    print("You pressed Ctrl+C!")
    window.destroy()
    close_window = True
    exit()

def on_closing(thread):
    # ask user if he wants to close the window using messagebox
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        global close_window
        global window
        close_window = True
        # kill thread
        window.destroy()
        system("kill -9 " + str(thread.ident))
        exit()



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


def askfile(button, chunk_size):
    global filename
    global DIRECTORY
    global year
    global month

    filename = (
        askopenfilename()
    )  # show an "Open" dialog box and return the path to the selected file
    if not filename:
        messagebox.showerror("Error", "No file selected")
        return

    if not filename.split("/")[-1].startswith(
        "PP_GUNICIISLEM.M."
    ) or not filename.split("/")[-1].endswith(".csv"):
        messagebox.showerror(
            "Error",
            filename.split("/")[-1]
            + " should start with PP_GUNICIISLEM.M. and end with .csv",
        )
        return

    year_month = filename.split("/")[-1].split(".")[2][0:6]
    year = year_month[0:4]
    month = year_month[4:]

    DIRECTORY = "data" + year + month

    button.config(
        text=filename.split("/")[-1] + " selected.\nClick to select another file"
    )


def process_file_g(progressed_chunk, process_file_button, select_file_button):
    global filename
    global DIRECTORY
    global year
    global month
    global chunk_size

    if not filename:
        messagebox.showerror("Error", "No file selected")
        return

    if path.exists(DIRECTORY):
        # ask user if he wants to overwrite existing data
        overwrite = messagebox.askyesno(
            "Overwrite",
            "Directory "
            + DIRECTORY
            + " already exists. Do you want to overwrite existing data?",
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

    process_file_button.config(text="Processing File...", state="disabled")
    select_file_button.config(state="disabled")

    
    i = 0

    # get total file size
    window.update()

    stop_flag = threading.Event()

    def process_file(chunk_size=chunk_size):
        nonlocal i
        nonlocal stop_flag
        nonlocal progressed_chunk
        print("Processing file started")

        for chunk in pd.read_csv(
            filename,
            chunksize=chunk_size.get() * GB,
            sep=";",
            low_memory=False,
        ):
            if close_window:
                break

            

            window.update()
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
                    filtered_data.to_csv(
                        name, sep=";", index=False, mode="a", header=False
                    )

            i += 1
            print("Chunk " + str(i + 1) + " processed")

            progressed_chunk.config(state="normal")
            progressed_chunk.delete(1.0, "end")
            progressed_chunk.insert(1.0, "Chunk " + str(i + 1) + " processed\n")
            progressed_chunk.config(state="disabled")


    thread = threading.Thread(target=process_file)
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(thread))

    thread.start()

    while thread.is_alive() and not stop_flag.is_set():
        window.update()

    stop_flag.set()

    thread.join()
    
    process_file_button.config(text="Process File", state="normal")
    select_file_button.config(state="normal")
    
    progressed_chunk.config(state="normal")
    progressed_chunk.delete(1.0, "end")
    progressed_chunk.insert(1.0, "Process Done\n")

    print("Done")


signal.signal(signal.SIGINT, signal_handler)


description_label = Label(
    window,
    text="Select a file to process - file name should \n be PP_GUNICIISLEM.M.{year}{month}.csv",
)
description_label.place(x=115, y=25)

chunk_size = Scale(
    window,
    from_=0.1,
    to=10,
    orient=HORIZONTAL,
    label="Chunk Size (in GB):",
    length=200,
    tickinterval=1,
    resolution=0.1,
)


file_button = Button(window, text="Select File")
file_button.config(command=lambda: askfile(file_button, chunk_size.get()))
file_button.pack(pady=75)

progressed_chunk = Text(window, height=3, width=20)
progressed_chunk.insert(1.0, "Enter File and \nClick Process File \nButton")
progressed_chunk.config(state="disabled")
progressed_chunk.place(x=170, y=210)

chunk_size.place(x=148, y=125)

process_file_button = Button(window, text="Process File")
process_file_button.config(
    command=lambda: process_file_g(progressed_chunk, process_file_button, file_button)
)
process_file_button.place(x=200, y=270)

# set resizable to false
window.resizable(False, False)
window.mainloop()
