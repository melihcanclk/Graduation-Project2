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

from custom_calendar import MyCalendar

from constants import *


pd.set_option("display.float_format", "{:.2f}".format)


day = "2023-04-03"


# plot data for time series
def plot_data(year, month, day, switch_var):
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

        # calculate the cA5 and cD5 coefficients
        cA5, cD5, cD4, cD3, cD2, cD1 = coeffs

        # normalize the coefficients
        cA5 = pywt.threshold(cA5, np.std(cA5), mode="soft")
        cD5 = pywt.threshold(cD5, np.std(cD5), mode="soft")
        cD4 = pywt.threshold(cD4, np.std(cD4), mode="soft")
        cD3 = pywt.threshold(cD3, np.std(cD3), mode="soft")
        cD2 = pywt.threshold(cD2, np.std(cD2), mode="soft")
        cD1 = pywt.threshold(cD1, np.std(cD1), mode="soft")

        # reconstruct the signal using the thresholded coefficients
        reconstructed_signal = pywt.waverec([cA5, cD5, cD4, cD3, cD2, cD1], wavelet)

        # remove negative values
        reconstructed_signal[reconstructed_signal < 0] = 0

        # plot the reconstructed signal
        fig, ax = plt.subplots(figsize=(15, 7))
        original_plot = ax.plot(data["ISLEM HACMI"], label="original signal")
        reconstructed_plot = ax.plot(reconstructed_signal, label="reconstructed signal")

        ## removable legend
        legend = plt.legend(loc="upper right")
        original_legend, reconstructed_legend = legend.get_lines()
        original_legend.set_picker(True)
        original_legend.set_pickradius(10)
        reconstructed_legend.set_picker(True)
        reconstructed_legend.set_pickradius(10)

        graphs = {}
        graphs[original_legend] = original_plot
        graphs[reconstructed_legend] = reconstructed_plot

        def onpick(event):
            _legend = event.artist

            _plot = graphs[_legend][0]

            visible = _plot.get_visible()
            _plot.set_visible(not visible)

            event.artist.set_visible(not visible)

            fig.canvas.draw()

        plt.connect("pick_event", onpick)

        ax.set_xlabel("Time(m)")
        ax.set_ylabel("Volume(₺)")
        # rotate x axis labels
        plt.xticks(rotation=90)
        # disappear legend on click
        ax.set_title("Wavelet - " + day)
        plt.show()
    else:
        # apply fast fourier transform to ISLEM HACMI
        fft_result = np.fft.fft(data["ISLEM HACMI"])

        # get frequency every second
        freq = np.fft.fftfreq(len(data["ISLEM HACMI"]))
        freq = freq * 86400

        # create new dataframe with fft result

        fft_data = pd.DataFrame(
            {
                "freq": freq,
                "fft": fft_result,
            }
        )

        # remove negative frequencies
        fft_data = fft_data[fft_data["freq"] > 0]

        # plot fft result
        fig, ax = plt.subplots(figsize=(15, 7))
        ax.plot(fft_data["freq"], np.abs(fft_data["fft"]))
        ax.set_xlabel("Frequency(Hz)")
        ax.set_ylabel("Amplitude")
        ax.set_title("FFT - " + day)
        plt.show()


window = Tk()
window.title("Graduation Project")
window.geometry("400x300")

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


# get selected date
def get_date():
    cal.get_displayed_month()
    # get date from calendar
    date = cal.selection_get()
    # seperate date into year, month, day
    year, month, day = str(date).split("-")
    # plot data
    plot_data(year, month, day, switch_var.get())


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


# create button to get date
Button(window, text="Get Date", command=get_date).pack()

window.mainloop()


# # apply fast fourier transform to ISLEM HACMI
# fft_result = np.fft.fft(data["ISLEM HACMI"])

# # get frequency every second
# freq = np.fft.fftfreq(len(data["ISLEM HACMI"]))
# freq = freq * 86400


# # create new dataframe with fft result

# fft_data = pd.DataFrame(
#     {
#         "freq": freq,
#         "fft": fft_result,
#     }
# )

# # remove negative frequencies
# fft_data = fft_data[fft_data["freq"] > 0]

# # plot fft result
# fig, ax = plt.subplots(figsize=(15, 7))
# ax.plot(fft_data["freq"], np.abs(fft_data["fft"]))
# ax.set_xlabel("Frequency(Hz)")
# ax.set_ylabel("Amplitude")
# ax.set_title("FFT")
# plt.show()


# print(data)

# # plot data for time series
# fig, ax = plt.subplots(figsize=(15, 7))

# #plot with dots
# ax.plot(data["ISLEM ZAMANI"], data["ISLEM HACMI"], "o", markersize=1)

# # x axis in minutes
# ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
# # format x axis
# ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

# #y axis in millions
# ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: "%dM" % (y * 1e-6)))

# ax.set_xlabel("Time(m)")
# ax.set_ylabel("Volume(₺)")
# # rotate x axis labels
# plt.xticks(rotation=90)
# ax.set_title("Volume by time")
# plt.show()
