from tkinter.messagebox import showerror
import pandas as pd


def precaution_time(first_hour, first_minute, second_hour, second_minute, year, month, day):
    if (
        first_hour == ""
        or first_minute == ""
        or second_hour == ""
        or second_minute == ""
    ):
        # show message box
        showerror("Error", "Time is empty")

        return False, False

    if (
        first_hour == "0"
        and first_minute == "0"
        and second_hour == "0"
        and second_minute == "0"
    ):
        # show message box
        showerror("Error", "Time is empty")

        return False, False

    # if second_hour or second_minute is not integer, show error
    if first_hour.isdigit() == False:
        # show message box
        showerror("Error", "Start Time Hour is not integer")

        return False, False

    if first_minute.isdigit() == False:
        # show message box
        showerror("Error", "Start Time Minute is not integer")

        return False, False

    if second_hour.isdigit() == False:
        # show message box
        showerror("Error", "End Time Hour or minute is not integer")

        return False, False

    if second_minute.isdigit() == False:
        # show message box
        showerror("Error", "End Time Minute is not integer")

        return  False, False

    if int(first_hour) > 23 or int(first_hour) < 0:
        # show message box
        showerror("Error", "Start Time Hour is not between 0 and 23")

        return False, False

    if int(first_minute) > 59 or int(first_minute) < 0:
        # show message box
        showerror("Error", "Start Time Minute is not between 0 and 59")

        return False, False

    if int(second_hour) > 23 or int(second_hour) < 0:
        # show message box
        showerror("Error", "End Time Hour is not between 0 and 23")

        return False, False

    if int(second_minute) > 59 or int(second_minute) < 0:
        # show message box
        showerror("Error", "End Time Minute is not between 0 and 59")

        return False, False

    # if first_hour or first_minute is not 2 digits, add 0 to the beginning
    if len(first_hour) == 1:
        first_hour = "0" + first_hour

    if len(first_minute) == 1:
        first_minute = "0" + first_minute

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

        return False, False

    # get difference between first_time and second_time
    difference = second_time - first_time

    if difference == pd.Timedelta(0):
        # show message box
        showerror("Error", "Time difference is 0")

        return False, False

    # if first time is less than 9:55, show error
    if first_time < pd.to_datetime(year + "-" + month + "-" + day + " 09:55"):
        # show message box
        showerror("Error", "First time is less than 9:55")

        return False, False

    # if second time is greater than 18:30, show error
    if second_time > pd.to_datetime(year + "-" + month + "-" + day + " 18:30"):
        # show message box
        showerror("Error", "Second time is greater than 18:30")

        return False, False
    
    return first_time, second_time