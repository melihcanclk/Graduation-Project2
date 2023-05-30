import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker

pd.set_option("display.float_format", "{:.2f}".format)

date = "202304"

CSV_WRITE_NAME = "data" + date + ".csv"


# read data from data.csv line by line
data = pd.read_csv(CSV_WRITE_NAME, sep=";", dtype=str, low_memory=False)

# remove milliseconds from ISLEM ZAMANI
data["ISLEM ZAMANI"] = data["ISLEM ZAMANI"].str.split(".", expand=True)[0]

# convert HACIM to float
data["HACIM"] = data["HACIM"].astype(float)

# sum HACIM by ISLEM ZAMANI
data = data.groupby("ISLEM ZAMANI").sum()

# convert data["DATE"] to str to plot
data.index = data.index.astype(str)

# plot data
plt.plot(data.index, data["HACIM"])
plt.xlabel("Time")

# set y axis to millions
plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
plt.ylabel("Volume(₺)")
plt.title("Volume by Time")
plt.show()