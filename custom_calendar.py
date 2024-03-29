import tkcalendar as tkc
import calendar


class MyCalendar(tkc.Calendar):
    def __init__(self, master=None, allowed_weekdays=(calendar.MONDAY,), **kw):
        self._disabled_dates = []
        self._select_only = allowed_weekdays
        tkc.Calendar.__init__(self, master, **kw)

        # change initially selected day if not right day
        if self._sel_date and not (self._sel_date.isoweekday() - 1) in allowed_weekdays:
            year, week, wday = self._sel_date.isocalendar()
            # get closest weekday
            next_wday = max(allowed_weekdays, key=lambda d: (d - wday + 1) > 0) + 1
            sel_date = self.date.fromisocalendar(
                year, week + int(next_wday < wday), next_wday
            )
            self.selection_set(sel_date)



    def disable_date(self, date):
        self._disabled_dates.append(date)
        mi, mj = self._get_day_coords(date)
        if mi is not None:  # date is displayed
            self._calendar[mi][mj].state(['disabled'])


    def _display_calendar(self):
        # display calendar
        tkc.Calendar._display_calendar(self)
        for date in self._disabled_dates:
            mi, mj = self._get_day_coords(date)
            if mi is not None:  # date is displayed
                self._calendar[mi][mj].state(['disabled'])

        # disable not allowed days
        for i in range(6):
            for j in range(7):
                if j in self._select_only:
                    continue
                self._calendar[i][j].state(["disabled"])


    def _prev_year(self):
        # disable years before 2023
        if self._date.year > 2023:
            tkc.Calendar._prev_year(self)

    def _prev_month(self):
        # disable months before 2023-01
        if self._date.year == 2023 and self._date.month <= 1:
            return
        tkc.Calendar._prev_month(self)

    def _next_year(self):
        # disable years after 2023
        if self._date.year < 2023:
            tkc.Calendar._next_year(self)

    def _next_month(self):
        # disable months after 2023-12
        if self._date.year == 2023 and self._date.month >= 12:
            return
        tkc.Calendar._next_month(self)


