import calendar
import unittest
from datetime import datetime, timedelta

from VisitTracker import VisitTracker


class VisitTrackerTestCase(unittest.TestCase):
    def setUp(self):
        self.tracker = VisitTracker()

    def test_get_day_total(self):
        date = datetime(2024, 1, 1).date()
        self.assertEqual(self.tracker.get_day_total(date), 0)

        # Simulate visits on the same day
        self.tracker.update(date, '192.168.0.1')
        self.tracker.update(date, '192.168.0.2')
        self.assertEqual(self.tracker.get_day_total(date), 2)

    def test_get_month_total(self):
        date = datetime(2024, 1, 1).date()
        self.assertEqual(self.tracker.get_month_total(date), 0)

        # Simulate visits in January
        for day in range(1, 30 + 1):
            self.tracker.update(datetime(2024, 1, day),
                                '192.168.0.1')
        self.assertEqual(self.tracker.get_month_total(date), 30)

    def test_get_yearly_total(self):
        date = datetime(2024, 1, 1).date()
        self.assertEqual(self.tracker.get_yearly_total(date), 0)

        # Simulate visits throughout the year
        days = 0
        for month in range(1, 13):
            _, num_days = calendar.monthrange(2024, month)
            for day in range(1, num_days + 1):
                days += 1
                self.tracker.update(datetime(2024, month, day),
                                    '192.168.0.1')
        self.assertEqual(self.tracker.get_yearly_total(date), days)

    def test_get_day_unique(self):
        date = datetime(2024, 1, 1).date()
        self.assertEqual(self.tracker.get_day_unique(date), 0)

        # Simulate visits on the same day with different IPs
        self.tracker.update(date, '192.168.0.1')
        self.tracker.update(date, '192.168.0.2')
        self.assertEqual(self.tracker.get_day_unique(date), 2)

    def test_get_month_unique(self):
        date = datetime(2024, 1, 1).date()
        self.assertEqual(self.tracker.get_month_unique(date), 0)

        # Simulate visits in January with different IPs
        for day in range(1, 31):
            self.tracker.update(datetime(2024, 1, day),
                                f'192.168.0.{day % 256}')
        self.assertEqual(self.tracker.get_month_unique(date), 30)

    def test_get_yearly_unique(self):
        date = datetime(2024, 1, 1).date()
        self.assertEqual(self.tracker.get_yearly_unique(date), 0)

        # Simulate visits throughout the 3 months with different IPs
        days = 0
        for month in range(1, 4):
            _, num_days = calendar.monthrange(2024, month)
            for day in range(1, num_days + 1):
                days += 1
                self.tracker.update(datetime(2024, month, day),
                                    f'192.168.0.{days % 256}')
        self.assertEqual(self.tracker.get_yearly_unique(date), days)

    def test_get_total_count(self):
        dates = [datetime(2023, 1, 1).date(),
                 datetime(2024, 2, 2).date(),
                 datetime(2024, 3, 3).date()]
        self.assertEqual(self.tracker.get_total_count(), 0)

        # Simulate visits on different dates from different clients
        self.tracker.update(dates[0], '192.168.0.1')
        self.tracker.update(dates[1], '192.168.0.1')
        self.tracker.update(dates[0], '192.168.0.2')
        self.tracker.update(dates[2], '192.168.0.2')
        self.tracker.update(dates[2], '192.168.0.3')
        self.assertEqual(self.tracker.get_total_count(), 5)

    def test_get_unique_count(self):
        dates = [datetime(2024, 1, 1).date(),
                 datetime(2024, 2, 2).date(),
                 datetime(2023, 3, 3).date()]
        self.assertEqual(self.tracker.get_unique_count(), 0)

        # Simulate visits on different dates from different clients
        self.tracker.update(dates[0], '192.168.0.1')
        self.tracker.update(dates[0], '192.168.0.2')
        self.tracker.update(dates[1], '192.168.0.2')
        self.tracker.update(dates[1], '192.168.0.3')
        self.tracker.update(dates[2], '192.168.0.4')
        self.tracker.update(dates[2], '192.168.0.5')
        self.assertEqual(self.tracker.get_unique_count(), 5)

    def test_update_data(self):
        date = datetime(2024, 1, 1).date()
        self.assertEqual(self.tracker.get_day_total(date), 0)

        # Simulate a single visit
        self.tracker.update(date, '192.168.0.1')
        self.assertEqual(self.tracker.get_day_total(date), 1)

        # Simulate multiple visits from the same IP
        for _ in range(5):
            self.tracker.update(date, '192.168.0.1')
        self.assertEqual(self.tracker.get_day_total(date), 6)

        # Simulate multiple visits from different IPs
        for i in range(1, 6):
            self.tracker.update(date, f'192.168.0.{i}')
        self.assertEqual(self.tracker.get_day_total(date), 11)
