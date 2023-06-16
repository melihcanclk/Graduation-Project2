from tkinter.messagebox import showerror
import pandas as pd
import matplotlib
import os

matplotlib.use("TkAgg")
import matplotlib.ticker as ticker
from tkinter import *

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# import wavelet for wavelet transform
import pywt

from scipy.stats import iqr, zscore
from custom_calendar import MyCalendar

from constants import *


pd.set_option("display.float_format", "{:.2f}".format)


day = "2023-04-03"


def calc_outliers(data, percentage_of_outliers=25):
    # apply outlier detection to fft_result using IQR
    q1 = np.quantile(data, percentage_of_outliers / 100)
    q3 = np.quantile(data, 1 - (percentage_of_outliers / 100))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # get outliers
    outliers = np.where((data > upper_bound) | (data < lower_bound))

    return outliers


# plot data for time series
def plot_data(year, month, day, switch_var, percentage_of_outliers=25.0):
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

    # convert ISLEM ZAMANI to datetime
    data["ISLEM ZAMANI"] = pd.to_datetime(data["ISLEM ZAMANI"], format="%H:%M:%S")

    if data.empty:
        # show message box
        showerror("Error", "Data is empty")

        return

    if switch_var == "TIME":
        # plot data for time series
        fig, ax = plt.subplots(figsize=(15, 7))

        # plot with dots
        ax.plot(data["ISLEM ZAMANI"], data["ISLEM HACMI"], "o", markersize=1)

        # x axis in minutes
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        # format x axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        # y axis in millions
        ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda y, pos: "%dM" % (y * 1e-6))
        )

        ax.set_xlabel("Time(m)")
        ax.set_ylabel("Volume(₺)")
        # rotate x axis labels
        plt.xticks(rotation=90)
        ax.set_title("Volume by time - " + day)
        plt.show()
    elif switch_var == "WAVE":
        wavelet = "db4"
        coeffs = pywt.wavedec(data["ISLEM HACMI"], wavelet=wavelet, level=5)

        # get outliers
        outliers = []

        outliers.append(calc_outliers(data["ISLEM HACMI"], percentage_of_outliers))

        for coeff in coeffs:
            outliers.append(calc_outliers(coeff, percentage_of_outliers))

        fig = plt.figure(figsize=(12, 7), layout="constrained")
        spec = fig.add_gridspec(4, 2)

        # plot data
        ax0 = fig.add_subplot(spec[0, :])
        ax0.plot(data["ISLEM ZAMANI"], data["ISLEM HACMI"], "b")
        ax0.plot(
            data.iloc[outliers[0]]["ISLEM ZAMANI"],
            data.iloc[outliers[0]]["ISLEM HACMI"],
            "o",
            markersize=1,
            color="red",
        )
        ax0.set_title("Volume by time - " + day)

        # plot coefficients in for loop by adding subplots
        for i in range(0, 3):
            for j in range(0, 2):
                ax = fig.add_subplot(spec[i + 1, j])
                ax.plot(coeffs[i + j], "b")
                ax.plot(
                    coeffs[i + j][outliers[i + j + 1]],
                    "o",
                    markersize=1,
                    color="red",
                )
                
                ax.set_title("Coefficients - " + str(i + 1) + str(j + 1))
            
        plt.show()

    else:
        # apply fast fourier transform to ISLEM HACMI
        fft_result = np.fft.fft(data["ISLEM HACMI"])

        # remove date from fft_result in ISLEM ZAMAANI
        data["ISLEM ZAMANI"] = data["ISLEM ZAMANI"].dt.time

        # get frequencies
        freq = np.fft.fftfreq(len(data["ISLEM HACMI"]))

        # get outliers
        outliers = calc_outliers(fft_result, percentage_of_outliers)

        # print when outliers occur in time series
        print(data.iloc[outliers])

        # plot fft_result with outliers
        fig, ax = plt.subplots(figsize=(15, 7))
        ax.plot(freq, fft_result, "o", markersize=1)

        # plot outliers
        ax.plot(freq[outliers], fft_result[outliers], "o", markersize=1, color="red")

        ax.set_xlabel("Frequency")
        ax.set_ylabel("Volume(₺)")
        ax.set_title("Volume by frequency - " + day)
        plt.show()


window = Tk()
window.title("Graduation Project")
window.geometry("400x400")

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
    from_=0,
    to=50,
    orient=HORIZONTAL,
    label="Percentage of outliers",
    length=200,
    tickinterval=10,
    resolution=1,
)


# get selected date
def get_date():
    cal.get_displayed_month()
    # get date from calendar
    date = cal.selection_get()
    # seperate date into year, month, day
    year, month, day = str(date).split("-")
    # plot data
    plot_data(year, month, day, switch_var.get(), percentage_of_outliers.get())


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


time_button.pack(side=LEFT)
freq_button.pack(side=LEFT)
wave_button.pack(side=LEFT)
percentage_of_outliers.pack()


# create button to get date
Button(window, text="Get Date", command=get_date).pack()


window.mainloop()
