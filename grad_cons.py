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

from pyod.models.iforest import IForest

# import wavelet for wavelet transform
import pywt

from custom_calendar import MyCalendar

from constants import *

from precaution import precaution_time

import mplcursors


pd.set_option("display.float_format", "{:.2f}".format)

def calc_IQR(data, percentage_of_outliers=25):
    # apply outlier detection using IQR algorithm
    q1 = np.quantile(data, percentage_of_outliers / 100)
    q3 = np.quantile(data, 1 - (percentage_of_outliers / 100))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # get outliers
    outliers = np.where((data > upper_bound) | (data < lower_bound))

    return outliers


# plot data for time series
def plot_data(
    year,
    month,
    day,
    switch_var,
    switch_algorithm_var,
    percentage_of_outliers,
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
        if switch_algorithm_var == "IQRCOV":
            # apply outlier detection to ISLEM HACMI using IQR
            outliers = calc_IQR(data["ISLEM HACMI"], percentage_of_outliers)

            # print when outliers occur in time series
            print(data.iloc[outliers])

            outliers = outliers[0]

        elif switch_algorithm_var == "PyOD":
             # apply outlier detection to ISLEM HACMI using PyOD

            contamination = percentage_of_outliers / 100

            data_array = np.array(data["ISLEM HACMI"]).reshape(-1, 1)
            clf = IForest(contamination=contamination)
            clf.fit(data_array)
            y_pred = clf.labels_

            # get outliers
            outliers = np.where(y_pred == 1)[0]

            # print when outliers occur in time series
            print(data.iloc[outliers])
        else: # for z-score
            # apply outlier detection to ISLEM HACMI using z-score
            z_scores = np.abs(data["ISLEM HACMI"] - np.mean(data["ISLEM HACMI"])) / np.std(data["ISLEM HACMI"])
            # use contamination to get outliers
            outliers = np.where(z_scores > 5 - percentage_of_outliers)[0]

            # print when outliers occur in time series
            print(data.iloc[outliers])

        # plot data and outliers
        fig, ax = plt.subplots(figsize=(15, 7))
        fig.canvas.manager.set_window_title("TIME - " + day)

        ax.plot(data["ISLEM ZAMANI"], data["ISLEM HACMI"], "o", markersize=1)
        # plot outliers
        ax.plot(
            data.iloc[outliers]["ISLEM ZAMANI"],
            data.iloc[outliers]["ISLEM HACMI"],
            "o",
            markersize=1,
            color="red",
        )

        # annotate outliers on hover
        annotations = []

        # add values to annotations
        for i in range(len(outliers)):
            annotations.append(
                ax.annotate(
                    data.iloc[outliers[i]]["ISLEM HACMI"],
                    (
                        data.iloc[outliers[i]]["ISLEM ZAMANI"],
                        data.iloc[outliers[i]]["ISLEM HACMI"],
                    ),
                    xytext=(
                        data.iloc[outliers[i]]["ISLEM ZAMANI"],
                        data.iloc[outliers[i]]["ISLEM HACMI"],
                    ),
                    textcoords="offset points",
                    size=10,
                    bbox=dict(boxstyle="round", fc="w"),
                )
            )

        # add hover functionality
        cursor = mplcursors.cursor(
            ax,
            hover=True,
        )

        # add annotations to cursor
        cursor.connect(
            "add",
            lambda sel: (
                sel.annotation.set_text(annotations[sel.index].get_text())
                if sel.annotation != None
                and sel.index < len(annotations)
                and sel.index >= 0
                else None
            ),
        )

        ax.set_xlabel("Time")
        ax.set_ylabel("Volume(₺)")
        ax.set_title("Volume by time - " + day)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        plt.show()

    elif switch_var == "FREQ":
        if switch_algorithm_var == "IQRCOV":
            # apply fast fourier transform to ISLEM HACMI
            fft_result = np.fft.fft(data["ISLEM HACMI"])

            # remove date from fft_result in ISLEM ZAMAANI
            data["ISLEM ZAMANI"] = data["ISLEM ZAMANI"].dt.time

            # get frequencies
            freq = np.fft.fftfreq(len(data["ISLEM HACMI"]))

            # get outliers
            outliers = calc_IQR(fft_result, percentage_of_outliers)
            outliers = outliers[0]

            # print when outliers occur in time series
            print(data.iloc[outliers])

        elif switch_algorithm_var == "PyOD":
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
        else:
            # apply fast fourier transform to ISLEM HACMI
            fft_result = np.fft.fft(data["ISLEM HACMI"])

            # remove date from fft_result in ISLEM ZAMAANI
            data["ISLEM ZAMANI"] = data["ISLEM ZAMANI"].dt.time

            # get frequencies
            freq = np.fft.fftfreq(len(data["ISLEM HACMI"]))

            # get outliers using z-score
            z_scores = np.abs(fft_result - np.mean(fft_result)) / np.std(fft_result)
            # use contamination to get outliers
            outliers = np.where(z_scores > 5 - percentage_of_outliers)[0]

            # print when outliers occur in time series
            print(data.iloc[outliers])

        # plot data and outliers in subplots besides power spectrum
        fig, axs = plt.subplots(2, sharex=False, figsize=(15, 7))
        fig.canvas.manager.set_window_title("FREQ - " + day)

        axs[0].plot(freq, fft_result.real, "o", markersize=1)
        # plot outliers
        axs[0].plot(
            freq[outliers],
            fft_result.real[outliers],
            "o",
            markersize=1,
            color="red",
        )

        # annotate outliers on hover
        annotations = []

        # add values to annotations
        for i in range(len(outliers)):
            annotations.append(
                axs[0].annotate(
                    data.iloc[outliers[i]]["ISLEM HACMI"],
                    (freq[outliers[i]], fft_result.real[outliers[i]]),
                    xytext=(freq[outliers[i]], fft_result.real[outliers[i]]),
                    textcoords="offset points",
                    size=10,
                    bbox=dict(boxstyle="round", fc="w"),
                )
            )

        # add hover functionality
        cursor = mplcursors.cursor(axs[0], hover=True)

        # add annotations to cursor
        cursor.connect(
            "add",
            lambda sel: (
                sel.annotation.set_text(annotations[sel.index].get_text())
                if sel.annotation != None
                and sel.index < len(annotations)
                and sel.index >= 0
                else None
            ),
        )

        axs[0].set_xlabel("Frequency")
        axs[0].set_ylabel("Volume(₺)")
        axs[0].set_title("Volume by frequency - " + day)

        axs[0].xaxis.set_major_formatter(ticker.FormatStrFormatter("%0.2f"))

        power_spectrum = np.abs(fft_result) ** 2

        axs[1].plot(freq, power_spectrum, "o", markersize=1)
        # plot outliers

        axs[1].plot(
            freq[outliers],
            power_spectrum[outliers],
            "o",
            markersize=1,
            color="red",
        )

        # annotate outliers on hover
        annotations = []

        # add values to annotations
        for i in range(len(outliers)):
            annotations.append(
                axs[1].annotate(
                    data.iloc[outliers[i]]["ISLEM HACMI"],
                    (freq[outliers[i]], power_spectrum[outliers[i]]),
                    xytext=(freq[outliers[i]], power_spectrum[outliers[i]]),
                    textcoords="offset points",
                    size=10,
                    bbox=dict(boxstyle="round", fc="w"),
                )
            )

        # add hover functionality
        cursor = mplcursors.cursor(axs[1], hover=True)

        # add annotations to cursor
        cursor.connect(
            "add",
            lambda sel: (
                sel.annotation.set_text(annotations[sel.index].get_text())
                if sel.annotation != None
                and sel.index < len(annotations)
                and sel.index >= 0
                else None
            ),
        )

        axs[1].set_xlabel("Frequency")
        axs[1].set_ylabel("Power")
        axs[1].set_title("Power spectrum - " + day)

        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.5)

        plt.show()

    else:
        wavelet = "db4"
        number_of_levels = 10

        data_outlier = []
        coeffs_outliers = []

        coeffs = pywt.wavedec(
            data["ISLEM HACMI"], wavelet=wavelet, level=number_of_levels
        )

        # reconstruct low frequency coefficients using upcoef
        coeffs[0] = pywt.upcoef(
            "a", coeffs[0], wavelet=wavelet, level=number_of_levels, take=len(data)
        )

        # reconstruct high frequency coefficients using upcoef
        for i in range(1, len(coeffs)):
            coeffs[i] = pywt.upcoef(
                "d", coeffs[i], wavelet=wavelet, level=(number_of_levels - i + 1), take=len(data)
            )


        if switch_algorithm_var == "IQRCOV":
            # apply outlier detection to data using IQR
            outliers = calc_IQR(data["ISLEM HACMI"], percentage_of_outliers)
            data_outlier.append(outliers)

            # reshape data outliers
            data_outlier = np.array(data_outlier).reshape(-1, 1)

            # apply outlier detection to coefficients using IQR
            for coeff in coeffs:
                outliers = calc_IQR(coeff, percentage_of_outliers)
                coeffs_outliers.append(outliers)

            for i in range(len(coeffs_outliers)):
                coeffs_outliers[i] = np.array(coeffs_outliers[i]).reshape(-1, 1)

        elif switch_algorithm_var == "PyOD":
            # apply outlier detection to data using PyOD
            contamination = percentage_of_outliers / 100
            data_array = np.array(data["ISLEM HACMI"]).reshape(-1, 1)
            clf = IForest(contamination=contamination)
            clf.fit(data_array)
            y_pred = clf.labels_
            data_outlier.append(np.where(y_pred == 1)[0])

            # apply outlier detection to coefficients using PyOD
            for coeff in coeffs:
                coeff_array = np.array(coeff).reshape(-1, 1)
                clf = IForest(contamination=contamination)
                clf.fit(coeff_array)
                y_pred = clf.labels_
                coeffs_outliers.append(np.where(y_pred == 1)[0])

        else: # for z-score
            # calculate z-score for data
            z_scores = np.abs(data["ISLEM HACMI"] - np.mean(data["ISLEM HACMI"])) / np.std(data["ISLEM HACMI"])

            # use contamination to get outliers
            data_outlier.append(np.where(z_scores > 5 - percentage_of_outliers)[0])

            # calculate z-score for coefficients
            for coeff in coeffs:
                z_scores = np.abs(coeff - np.mean(coeff)) / np.std(coeff)
                # use contamination to get outliers
                coeffs_outliers.append(np.where(z_scores > 5 - percentage_of_outliers)[0])

        # print when outliers occur in time series
        print(data.iloc[data_outlier[0]])

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

        # annotate outliers on hover
        annotations = []

        # add values to annotations
        for i in range(len(data_outlier[0])):
            annotations.append(
                axs[0].annotate(
                    data.iloc[data_outlier[0][i]]["ISLEM HACMI"],
                    (
                        data.iloc[data_outlier[0][i]]["ISLEM ZAMANI"],
                        data.iloc[data_outlier[0][i]]["ISLEM HACMI"],
                    ),
                    xytext=(
                        data.iloc[data_outlier[0][i]]["ISLEM ZAMANI"],
                        data.iloc[data_outlier[0][i]]["ISLEM HACMI"],
                    ),
                    textcoords="offset points",
                    size=10,
                    bbox=dict(boxstyle="round", fc="w"),
                )
            )

        # add hover functionality
        cursor = mplcursors.cursor(axs[0], hover=True)

        # add annotations to cursor
        cursor.connect(
            "add",
            lambda sel: (
                sel.annotation.set_text(annotations[sel.index].get_text())
                if sel.annotation != None
                and sel.index < len(annotations)
                and sel.index >= 0
                else None
            ),
        )

        axs[0].set_xlabel("Time")
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

            # annotate outliers on hover
            annotations = []

            # add values to annotations
            for j in range(len(coeffs_outliers[i])):
                annotations.append(
                    axs[i + 1].annotate(
                        coeffs[i][coeffs_outliers[i][j]],
                        (coeffs_outliers[i][j], coeffs[i][coeffs_outliers[i][j]]),
                        xytext=(
                            coeffs_outliers[i][j],
                            coeffs[i][coeffs_outliers[i][j]],
                        ),
                        textcoords="offset points",
                        size=10,
                        bbox=dict(boxstyle="round", fc="w"),
                    )
                )

            # add hover functionality
            cursor = mplcursors.cursor(axs[i + 1], hover=True)

            # add annotations to cursor
            cursor.connect (
                "add",
                lambda sel: (
                    sel.annotation.set_text(annotations[sel.index].get_text())  
                    if sel.annotation != None
                    and sel.index < len(annotations)
                    and sel.index >= 0
                    else None
                ),
            )


            axs[i + 1].set_xlabel("Time")
            axs[i + 1].set_ylabel("Coefficient " + str(i + 1), rotation=0, labelpad=40)
            axs[i + 1].yaxis.set_label_position("left")

        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.5)
        plt.show()


window = Tk()
window.title("Graduation Project")
window.geometry("500x550")

# set resizable to false
window.resizable(False, False)

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
    to=4.9,
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

    first_time, second_time = precaution_time(
        first_hour=first_hour,
        first_minute=first_minute,
        second_hour=second_hour,
        second_minute=second_minute,
        year=year,
        month=month,
        day=day,
    )

    if not first_time or not second_time:
        return

    plot_data(
        year,
        month,
        day,
        switch_var.get(),
        switch_algorithm_var.get(),
        percentage_of_outliers.get(),
        first_time,
        second_time,
    )


# display calendar
cal.pack(pady=20)

## create frame for radio buttons

label_graph = Label(window, text="Graph")
label_graph.pack()

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

## create frame for algorithms
algorithm_label = Label(window, text="Algorithm")
algorithm_label.pack(pady=(10, 0))

switch_frame_algorithm = Frame(window)
switch_frame_algorithm.pack()

switch_algorithm_var = StringVar(value="PyOD")

pyod_iforest_button = Radiobutton(
    switch_frame_algorithm,
    text="PyOD - IForest",
    variable=switch_algorithm_var,
    value="PyOD",
)
iqrcov_button = Radiobutton(
    switch_frame_algorithm,
    text="IQRCOV",
    variable=switch_algorithm_var,
    value="IQRCOV",
)
z_score_button = Radiobutton(
    switch_frame_algorithm,
    text="Z-Score",
    variable=switch_algorithm_var,
    value="Z-Score",
)


## create frame for time spinboxes
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

## pack radio buttons for time, frequency and wavelet
time_button.pack(side=LEFT)
freq_button.pack(side=LEFT)
wave_button.pack(side=LEFT)

## pack radio buttons for algorithms
pyod_iforest_button.pack(side=LEFT)
iqrcov_button.pack(side=LEFT)
z_score_button.pack(side=LEFT)

## pack percentage of outliers
percentage_of_outliers.pack()


# create button to get date
Button(window, text="Plot Graph", command=get_date).pack()


window.mainloop()
