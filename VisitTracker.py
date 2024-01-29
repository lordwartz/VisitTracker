import calendar
from datetime import datetime
from collections import Counter, defaultdict


class VisitTracker:
    def __init__(self, stats=None):
        if stats is None:
            stats = (defaultdict(defaultdict(defaultdict(defaultdict(Counter)))))
        self.stats = stats
        self._unique_visitors = set()
        self._total_visits = 0

    def get_day_total(self, date):
        return sum(sum(hour_counter.values())
                   for hour_counter in
                   self.stats[date.year][date.month][date.day].values())

    def get_month_total(self, date):
        month_total = 0
        for day in self.stats[date.year][date.month].keys():
            curr_day = datetime(date.year, date.month, day)
            month_total += self.get_day_total(curr_day)

        return month_total

    def get_yearly_total(self, date):
        yearly_total = 0
        for month in self.stats[date.year].keys():
            curr_month = datetime(date.year, month, 1)
            yearly_total += self.get_month_total(curr_month)

        return yearly_total

    def get_total_count(self):
        return self._total_visits

    def get_day_unique(self, date):
        unique = set()
        for hour_counter in \
                (self.stats[date.year][date.month][date.day].values()):
            for ip in hour_counter.keys():
                unique.add(ip)
        return len(unique)

    def get_month_unique(self, date):
        begin = datetime(date.year, date.month, 1)
        end = datetime(date.year, date.month,
                       calendar.monthrange(date.year, date.month)[1], 23)
        range_data = [data[0] for data in
                      self._get_united_range_data(begin, end)]
        return len(set(range_data))

    def get_yearly_unique(self, date):
        begin = datetime(date.year, 1, 1)
        end = datetime(date.year, 12,
                       calendar.monthrange(date.year, 12)[1], 23)
        range_data = [data[0] for data in
                      self._get_united_range_data(begin, end)]
        return len(set(range_data))

    def get_unique_count(self):
        return len(self._unique_visitors)

    def update(self, date, ip):
        self.stats[date.year][date.month][date.day][date.hour][ip] += 1
        self._unique_visitors.add(ip)
        self._total_visits += 1

    def _get_united_range_data(self, begin, end):
        data = list()
        if begin < end:
            for year in range(begin.year, end.year + 1):
                start_month, end_month = 1, 12
                if year == begin.year:
                    start_month = begin.month
                if year == end.year:
                    end_month = end.month
                for month in range(start_month, end_month + 1):
                    _, month_len = calendar.monthrange(year, month)
                    start_day, end_day = 1, month_len
                    if month == begin.month:
                        start_day = begin.day
                    if month == end.month:
                        end_day = end.day
                    for day in range(start_day, end_day + 1):
                        start_hour, end_hour = 0, 23
                        if day == begin.day:
                            start_hour = begin.hour
                        if day == end.day:
                            end_hour = end.hour
                        for hour in range(start_hour, end_hour + 1):
                            if (len(self.stats[year][month][day][hour].keys())
                                    != 0):
                                hour_counter = (
                                    self.stats)[year][month][day][hour]
                                for ip, count in hour_counter.items():
                                    data.append((ip, count))
        return data
