from datetime import datetime
from collections import Counter


class VisitTracker:
    def __init__(self, stats=None):
        if stats is None:
            stats = {}
        self.stats = stats

    def get_day_total(self, date: datetime.date):
        return 0 if date not in self.stats.keys() \
            else sum(self.stats[date].values())

    def get_month_total(self, date: datetime.date):
        month_total = 0
        for existed_date in self.stats.keys():
            if (existed_date.year == date.year and
                    existed_date.month == date.month):
                month_total += self.get_day_total(existed_date)

        return month_total

    def get_yearly_total(self, date: datetime.date):
        return sum(self.get_month_total(datetime(date.year, month, 1))
                   for month in range(1, 12 + 1))

    def get_total_count(self):
        total = 0
        for existed_date in self.stats.keys():
            total += sum(self.stats[existed_date].values())
        return total

    def get_day_unique(self, date: datetime.date):
        return len(self.stats[date]) if date in self.stats.keys() else 0

    def get_month_unique(self, date: datetime.date):
        unique = set()
        for existed_date in self.stats.keys():
            if (existed_date.year == date.year and
                    existed_date.month == date.month):
                for ip in self.stats[existed_date].keys():
                    unique.add(ip)

        return len(unique)

    def get_yearly_unique(self, date: datetime.date):
        unique = set()
        for existed_date in self.stats.keys():
            if existed_date.year == date.year:
                for ip in self.stats[existed_date].keys():
                    unique.add(ip)
        return len(unique)

    def get_unique_count(self):
        unique = set()
        for existed_date in self.stats.keys():
            for ip in self.stats[existed_date].keys():
                unique.add(ip)
        return len(unique)

    def update(self, date: datetime.date, ip):
        if date not in self.stats:
            self.stats[date] = Counter()
        self.stats[date][ip] += 1
