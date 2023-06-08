# Graduation-Project2
2nd Semester Graduation Project Source Codes

## 1. Introduction
Project uses Borsa Istanbul's Intraday Transaction Book Information and process them with Fourier Transform to find the most dominant frequencies. 

## 2. Requirements
* Python 3.6
* Numpy
* Pandas
* Matplotlib 2.2
* Scipy
* PyQT 5.9.2
* Python 3 TK

## 3. Installation
* Install Python 3.6
``` bash
sudo apt-get install python3.6
```

* Install pip3
``` bash
sudo apt-get install python3-pip
```

* Install Numpy
``` bash
pip3 install numpy
```

* Install Pandas
``` bash
pip3 install pandas
```

* Install Matplotlib
``` bash
pip3 install matplotlib
```

* Install Scipy
``` bash
pip3 install scipy
```

* Install PyQT5
``` bash
pip3 install PyQt5==5.9.2
```

* Install Python 3 TK

for Ubuntu
``` bash
sudo apt-get install python3-tk
```

for Fedora
``` bash
sudo dnf install python3-tkinter
```

## 4. Usage
There are two type of python file in this project. First one (grad_prod) used to get Borsa Istanbul's Intraday Transaction Book Information and collect all the data in a .csv files with their date. Second one (grad_cons) used to process the data with Fourier Transform and plot the results.

Note: constants.py includes all the constants that used in both grad_prod and grad_cons, it includes holiday days and their calculations.


