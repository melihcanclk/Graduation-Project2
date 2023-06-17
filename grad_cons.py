from tkinter.messagebox import showerror
import pandas as pd
import matplotlib
import os

matplotlib.use("TkAgg")
import matplotlib.ticker as ticker
from tkinter import *

from tkinter import ttk

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from pyod.models.iforest import IForest
from pyod.utils.data import evaluate_print
from pyod.utils.data import generate_data
from pyod.utils.example import visualize

# import wavelet for wavelet transform
import pywt

from scipy.stats import iqr, zscore
from custom_calendar import MyCalendar

from constants import *


pd.set_option("display.float_format", "{:.2f}".format)


day = "2023-04-03"


# plot data for time series
def plot_data(
    year,
    month,
    day,
    switch_var,
    percentage_of_outliers=25.0,
    first_time=None,
    second_time=None,
):
    # create day string
    day = year + "-" + month + "-" + day

    data = pd.DataFrame(
        {
            "TARIH": [],
            "ISLEM ZAMANI": [],
            "ISLEM HACMI": [],
        }
    )

    name = "data" + year + month + "/" + day + ".csv"

    # if csv file with name day + CSV_WRITE_NAME doesnt exist, show error modal
    if not os.path.isfile(name):
        # show message box
        showerror("Error", "File doesnt exist")

        return

    for chunk in pd.read_csv(name, sep=";", low_memory=False, chunksize=CHUNK_SIZE):
        # append chunk to data
        data = pd.concat([data, chunk], ignore_index=True)
        print("Chunk appended")

    # add ISLEM HACMI if ISLEM ZAMANI is the same
    data = data.groupby(["TARIH", "ISLEM ZAMANI"])["ISLEM HACMI"].sum().reset_index()

    # remove dates from first_time and second_time
    first_time = first_time.strftime("%H:%M:%S")
    second_time = second_time.strftime("%H:%M:%S")

    # filter data by first_time and second_time
    data = data[
        (data["ISLEM ZAMANI"] >= first_time) & (data["ISLEM ZAMANI"] <= second_time)
    ]

    if data.empty:
        # show message box
        showerror("Error", "No data in this time range")

        return

    # convert ISLEM ZAMANI to datetime
    data["ISLEM ZAMANI"] = pd.to_datetime(data["ISLEM ZAMANI"], format="%H:%M:%S")

    if switch_var == "TIME":
        # apply outlier detection to ISLEM HACMI using PyOD

        contamination = percentage_of_outliers / 100

        data_array = np.array(data["ISLEM HACMI"]).reshape(-1, 1)
        clf = IForest(contamination=contamination)
        clf.fit(data_array)
        y_pred = clf.labels_
        y_scores = clf.decision_scores_

        # get outliers
        outliers = np.where(y_pred == 1)[0]

        # print when outliers occur in time series
        print(data.iloc[outliers])

        fig, ax = plt.subplots(figsize=(15, 7))
        fig.canvas.manager.set_window_title("TIME - " + day)
        ax.plot(data["ISLEM ZAMANI"], data["ISLEM HACMI"], "b")
        ax.plot(
            data.iloc[outliers]["ISLEM ZAMANI"],
            data.iloc[outliers]["ISLEM HACMI"],
            "o",
            markersize=1,
            color="red",
        )

        # set x axis to time
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        ax.tick_params(axis="x", rotation=45)

        ax.set_xlabel("Time")
        ax.set_ylabel("Volume(₺)")
        ax.set_title("Volume by time - " + day)

        plt.show()

    elif switch_var == "WAVE":
        wavelet = "db4"
        number_of_levels = 6
        coeffs = pywt.wavedec(
            data["ISLEM HACMI"], wavelet=wavelet, level=number_of_levels
        )

        data_outlier = []
        coeffs_outliers = []

        # apply outlier detection to data using PyOD
        contamination = percentage_of_outliers / 100
        data_array = np.array(data["ISLEM HACMI"]).reshape(-1, 1)
        clf = IForest(contamination=contamination)
        clf.fit(data_array)
        y_pred = clf.labels_
        y_scores = clf.decision_scores_
        data_outlier.append(np.where(y_pred == 1)[0])

        # apply outlier detection to coefficients using PyOD
        for coeff in coeffs:
            coeff_array = np.array(coeff).reshape(-1, 1)
            clf = IForest(contamination=contamination)
            clf.fit(coeff_array)
            y_pred = clf.labels_
            y_scores = clf.decision_scores_
            coeffs_outliers.append(np.where(y_pred == 1)[0])

        # plot data and coefficients in subplots
        fig, axs = plt.subplots(len(coeffs) + 1, sharex=False, figsize=(20, 12))
        fig.canvas.manager.set_window_title("WAVELET - " + day)

        # plot data
        axs[0].plot(data["ISLEM ZAMANI"], data["ISLEM HACMI"], "b")
        axs[0].plot(
            data.iloc[data_outlier[0]]["ISLEM ZAMANI"],
            data.iloc[data_outlier[0]]["ISLEM HACMI"],
            "o",
            markersize=1,
            color="red",
        )
        axs[0].set_ylabel("Volume(₺)", rotation=0, labelpad=40)
        axs[0].yaxis.set_label_position("left")
        axs[0].set_title("Volume by time - " + day)

        axs[0].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        # plot coefficients
        for i in range(len(coeffs)):
            axs[i + 1].plot(coeffs[i], "b")
            axs[i + 1].plot(
                coeffs_outliers[i],
                coeffs[i][coeffs_outliers[i]],
                "o",
                markersize=2,
                color="red",
            )
            axs[i + 1].set_ylabel("Coefficient " + str(i + 1), rotation=0, labelpad=40)
            axs[i + 1].yaxis.set_label_position("left")

        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.5)
        plt.show()

    else:
        # apply fast fourier transform to ISLEM HACMI
        fft_result = np.fft.fft(data["ISLEM HACMI"])

        # remove date from fft_result in ISLEM ZAMAANI
        data["ISLEM ZAMANI"] = data["ISLEM ZAMANI"].dt.time

        # get frequencies
        freq = np.fft.fftfreq(len(data["ISLEM HACMI"]))

        contamination = percentage_of_outliers / 100

        clf = IForest(contamination=contamination)

        # convert fft_result values into real numbers
        fft_result_abs = fft_result.real

        fft_result_abs = np.array(fft_result_abs).reshape(-1, 1)

        clf.fit(fft_result_abs)
        y_pred = clf.labels_

        # get outliers
        outliers = np.where(y_pred == 1)[0]

        # print when outliers occur in time series
        print(data.iloc[outliers])

        # plot fft_result with outliers
        fig, ax = plt.subplots(figsize=(15, 7))
        fig.canvas.manager.set_window_title("FREQUENCY - " + day)
        ax.plot(freq, fft_result, "o", markersize=1)

        # plot outliers
        ax.plot(freq[outliers], fft_result[outliers], "o", markersize=1, color="red")

        ax.set_xlabel("Frequency")
        ax.set_ylabel("Volume(₺)")
        ax.set_title("Volume by frequency - " + day)
        plt.show()


window = Tk()
window.title("Graduation Project")
window.geometry("500x500")

# set resizable to false
window.resizable(False, False)

# seperate day into year, month, day
year, month, day = day.split("-")

time_now = pd.to_datetime("now")
# create calendar

cal = MyCalendar(
    window,
    allowed_weekdays=(0, 1, 2, 3, 4),
    weekendbackground="white",
    weekendforeground="black",
    othermonthbackground="gray95",
    othermonthwebackground="gray95",
    othermonthforeground="black",
    othermonthweforeground="black",
    displayeddaybackground="red",
    maxdate=time_now,
    firstweekday="monday",
    disable_days=holidays,
    showothermonthdays=False,
)

# call disable_date for every holiday
for holiday in holidays:
    cal.disable_date(holiday)

percentage_of_outliers = Scale(
    window,
    from_=0.1,
    to=10,
    orient=HORIZONTAL,
    label="Percentage of outliers",
    length=200,
    tickinterval=1,
    resolution=0.1,
)


# get selected date
def get_date():
    cal.get_displayed_month()
    # get date from calendar
    date = cal.selection_get()
    # seperate date into year, month, day
    year, month, day = str(date).split("-")
    # plot data

    # get time from spinboxes
    first_hour = hours_spinbox.get()
    first_minute = minutes_spinbox.get()

    second_hour = hours_spinbox2.get()
    second_minute = minutes_spinbox2.get()

    # if first_hour or first_minute is not 2 digits, add 0 to the beginning
    if len(first_hour) == 1:
        first_hour = "0" + first_hour

    if len(first_minute) == 1:
        first_minute = "0" + first_minute

    # if second_hour or second_minute is not integer, show error
    if first_hour.isdigit() == False:
        # show message box
        showerror("Error", "Start Time Hour is not integer")

        return

    if first_minute.isdigit() == False:
        # show message box
        showerror("Error", "Start Time Minute is not integer")

        return

    if second_hour.isdigit() == False:
        # show message box
        showerror("Error", "End Time Hour or minute is not integer")

        return

    if second_minute.isdigit() == False:
        # show message box
        showerror("Error", "End Time Minute is not integer")

        return

    # create datetime objects
    first_time = pd.to_datetime(
        year + "-" + month + "-" + day + " " + first_hour + ":" + first_minute
    )

    second_time = pd.to_datetime(
        year + "-" + month + "-" + day + " " + second_hour + ":" + second_minute
    )

    # check if first_time is greater than second_time
    if first_time > second_time:
        # show message box
        showerror("Error", "First time is greater than second time")

        return

    # get difference between first_time and second_time
    difference = second_time - first_time

    if difference == pd.Timedelta(0):
        # show message box
        showerror("Error", "Time difference is 0")

        return

    # if first time is less than 9:55, show error
    if first_time < pd.to_datetime(year + "-" + month + "-" + day + " 09:55"):
        # show message box
        showerror("Error", "First time is less than 9:55")

        return

    # if second time is greater than 18:30, show error
    if second_time > pd.to_datetime(year + "-" + month + "-" + day + " 18:30"):
        # show message box
        showerror("Error", "Second time is greater than 18:30")

        return

    plot_data(
        year,
        month,
        day,
        switch_var.get(),
        percentage_of_outliers.get(),
        first_time,
        second_time,
    )


# display calendar
cal.pack(pady=20)

switch_frame = Frame(window)
switch_frame.pack()
switch_var = StringVar(value="TIME")

time_button = Radiobutton(switch_frame, text="Time", variable=switch_var, value="TIME")
freq_button = Radiobutton(
    switch_frame, text="Frequency", variable=switch_var, value="FREQ"
)
wave_button = Radiobutton(
    switch_frame, text="Wavelet", variable=switch_var, value="WAVE"
)

time_frame = Frame(window)
time_frame.pack(padx=20, pady=10)

label = Label(time_frame, text="Start time")
label.pack(side=LEFT)

hours_spinbox = Spinbox(
    time_frame, from_=0, to=23, width=4, textvariable=StringVar(value="9")
)
hours_spinbox.pack(side=LEFT)

seperator = Label(time_frame, text=":")
seperator.pack(side=LEFT)

minutes_spinbox = Spinbox(
    time_frame, from_=0, to=59, width=4, textvariable=StringVar(value="55")
)
minutes_spinbox.pack(side=LEFT)

time_frame = Frame(window)
time_frame.pack(padx=20, pady=10)

label = Label(time_frame, text="End time")
label.pack(side=LEFT)

hours_spinbox2 = Spinbox(
    time_frame, from_=0, to=23, width=4, textvariable=StringVar(value="18")
)
hours_spinbox2.pack(side=LEFT)

seperator2 = Label(time_frame, text=":")
seperator2.pack(side=LEFT)

minutes_spinbox2 = Spinbox(
    time_frame, from_=0, to=59, width=4, textvariable=StringVar(value="30")
)
minutes_spinbox2.pack(side=LEFT)


time_button.pack(side=LEFT)
freq_button.pack(side=LEFT)
wave_button.pack(side=LEFT)
percentage_of_outliers.pack()


# create button to get date
Button(window, text="Get Date", command=get_date).pack()


window.mainloop()
