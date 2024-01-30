import calendar
import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from visit_tracker import VisitTracker
from database.visit_model import Base, Visit


class VisitTrackerTestCase(unittest.TestCase):
    def setUp(self):
        self.db_path = "sqlite:///test_visits.db"
        self.tracker = VisitTracker(self.db_path)
        engine = create_engine(self.db_path)
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.session.query(Visit).delete()
        self.session.commit()

    def tearDown(self):
        self.tracker.session.close()

    def test_model_repr(self):
        visit = Visit(datetime(2022, 1, 1, 13, 15), '192.168.0.1')

        self.assertEqual("<Visit date: 2022-01-01 13:15:00, ip: 192.168.0.1>",
                         str(visit))

    def test_update_data(self):
        dates = [datetime(2024, 1, 1, 1, 1),
                 datetime(2024, 1, 1, 1, 2),
                 datetime(2024, 1, 1, 1, 3),
                 datetime(2024, 1, 1, 1, 4),
                 datetime(2024, 1, 1, 1, 5),
                 datetime(2024, 1, 1, 1, 6)]
        self.assertEqual(0, self.tracker.get_daily_total(dates[0]))

        # Simulate a single visit
        self.tracker.update(dates[0], '192.168.0.1')
        self.assertEqual(1, self.tracker.get_daily_total(dates[0]))

        # Simulate multiple visits from the same IP
        for i in range(1, 3):
            self.tracker.update(dates[i], '192.168.0.1')
        self.assertEqual(3, self.tracker.get_daily_total(dates[0]))

        # Simulate multiple visits from different IPs
        for i in range(3, 6):
            self.tracker.update(dates[i], f'192.168.0.{i}')
        self.assertEqual(6, self.tracker.get_daily_total(dates[0]))

    def test_get_day_total(self):
        dates = [datetime(2024, 1, 1, 1, 1, 1),
                 datetime(2024, 1, 1, 1, 1, 2)]
        self.assertEqual(0, self.tracker.get_daily_total(dates[0]))

        # Simulate visits on the same day
        self.tracker.update(dates[0], '192.168.0.1')
        self.tracker.update(dates[1], '192.168.0.2')
        self.assertEqual(2, self.tracker.get_daily_total(dates[0]))

    def test_get_month_total(self):
        date = datetime(2024, 1, 1, 1, 1)
        self.assertEqual(0, self.tracker.get_monthly_total(date))

        # Simulate visits in January
        for day in range(1, 30 + 1):
            self.tracker.update(datetime(2024, 1, day),
                                '192.168.0.1')
        self.assertEqual(30, self.tracker.get_monthly_total(date))

    def test_get_yearly_total(self):
        date = datetime(2024, 1, 1, 1, 1)
        self.assertEqual(0, self.tracker.get_yearly_total(date))

        # Simulate visits throughout the year
        days = 0
        for month in range(1, 13):
            _, num_days = calendar.monthrange(2024, month)
            for day in range(1, num_days + 1):
                days += 1
                self.tracker.update(datetime(2024, month, day),
                                    '192.168.0.1')
        self.assertEqual(days, self.tracker.get_yearly_total(date))

    def test_get_day_unique(self):
        dates = [datetime(2024, 1, 1, 1, 1),
                 datetime(2024, 1, 1, 1, 2)]
        self.assertEqual(0, self.tracker.get_day_unique(dates[0]))

        # Simulate visits on the same day with different IPs
        self.tracker.update(dates[0], '192.168.0.1')
        self.tracker.update(dates[1], '192.168.0.2')
        self.assertEqual(2, self.tracker.get_day_unique(dates[0]))

    def test_get_month_unique(self):
        date = datetime(2024, 1, 1, 1, 1)
        self.assertEqual(0, self.tracker.get_month_unique(date))

        # Simulate visits in January with different IPs
        for day in range(1, 31):
            self.tracker.update(datetime(2024, 1, day),
                                f'192.168.0.{day % 256}')
        self.assertEqual(30, self.tracker.get_month_unique(date))

    def test_get_yearly_unique(self):
        date = datetime(2024, 1, 1, 1, 1)
        self.assertEqual(0, self.tracker.get_yearly_unique(date))

        # Simulate visits throughout the 3 months with different IPs
        days = 0
        for month in range(1, 4):
            _, num_days = calendar.monthrange(2024, month)
            for day in range(1, num_days + 1):
                days += 1
                self.tracker.update(datetime(2024, month, day),
                                    f'192.168.0.{days % 256}')
        self.assertEqual(days, self.tracker.get_yearly_unique(date))

    def test_get_total_count(self):
        self.assertEqual(0, self.tracker.get_total_count())

        # Simulate visits on different dates from different clients
        self.tracker.update(datetime(2023, 1, 1, 1, 1), '192.168.0.1')
        self.tracker.update(datetime(2023, 1, 1, 1, 2), '192.168.0.1')
        self.tracker.update(datetime(2023, 1, 2, 1, 1), '192.168.0.2')
        self.tracker.update(datetime(2024, 2, 2, 1, 1), '192.168.0.2')
        self.tracker.update(datetime(2024, 3, 3, 1, 1), '192.168.0.3')
        self.assertEqual(5, self.tracker.get_total_count())

    def test_get_unique_count(self):
        self.assertEqual(0, self.tracker.get_unique_count())

        # Simulate visits on different dates from different clients
        self.tracker.update(datetime(2023, 1, 1, 1, 1), '192.168.0.1')
        self.tracker.update(datetime(2023, 2, 1, 1, 1), '192.168.0.2')
        self.tracker.update(datetime(2023, 3, 1, 1, 1), '192.168.0.2')
        self.tracker.update(datetime(2024, 1, 1, 1, 1), '192.168.0.3')
        self.tracker.update(datetime(2024, 2, 1, 1, 1), '192.168.0.4')
        self.tracker.update(datetime(2024, 3, 1, 1, 1), '192.168.0.5')
        self.assertEqual(5, self.tracker.get_unique_count())

    def test_get_total_on_range(self):
        # Simulate multiple visits at different times
        self.tracker.update(datetime(2022, 1, 1, 14), '192.168.0.1')
        self.tracker.update(datetime(2022, 1, 2, 10), '192.168.0.2')
        self.tracker.update(datetime(2022, 1, 3, 20), '192.168.0.3')

        start_date = datetime(2022, 1, 1, 7)
        end_date = datetime(2022, 1, 3, 15)
        self.assertEqual(2, self.tracker.get_total_on_range(start_date,
                                                            end_date))

    def test_get_unique_on_range(self):
        # Simulate multiple visits at different times
        self.tracker.update(datetime(2022, 1, 1, 14), '192.168.0.1')
        self.tracker.update(datetime(2022, 1, 3, 10), '192.168.0.2')
        self.tracker.update(datetime(2022, 2, 10, 5), '192.168.0.2')
        self.tracker.update(datetime(2022, 3, 1, 12), '192.168.0.3')

        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 2, 25)
        self.assertEqual(2, self.tracker.get_unique_on_range(start_date,
                                                             end_date))

    def test_get_stats_by_hours(self):
        # Simulate multiple visits at different times
        self.tracker.update(datetime(2022, 1, 1, 13, 15), '192.168.0.1')
        self.tracker.update(datetime(2022, 1, 1, 13, 2), '192.168.0.2')
        self.tracker.update(datetime(2022, 1, 1, 14, 30), '192.168.0.3')
        self.tracker.update(datetime(2022, 1, 1, 14, 45), '192.168.0.3')
        self.tracker.update(datetime(2022, 1, 1, 15, 45), '192.168.0.4')
        self.tracker.update(datetime(2022, 1, 2, 10, 0), '192.168.0.4')

        hourly_stats = (self.tracker.get_stats_by_resolution(
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            'hour'))
        self.assertEqual(3, len(hourly_stats))

        # Check the statistics for each hour
        self.assertEqual(2, hourly_stats[0][1])
        self.assertEqual(2, hourly_stats[0][2])
        self.assertEqual(2, hourly_stats[1][1])
        self.assertEqual(1, hourly_stats[1][2])
        self.assertEqual(1, hourly_stats[2][1])
        self.assertEqual(1, hourly_stats[2][2])

    def test_get_stats_by_days(self):
        self.tracker.update(datetime(2022, 1, 1, 13, 15), '192.168.0.1')
        self.tracker.update(datetime(2022, 1, 2, 14, 2), '192.168.0.2')
        self.tracker.update(datetime(2022, 1, 2, 15, 30), '192.168.0.3')
        self.tracker.update(datetime(2022, 1, 3, 16, 45), '192.168.0.4')
        self.tracker.update(datetime(2022, 1, 3, 10, 0), '192.168.0.4')
        self.tracker.update(datetime(2022, 3, 4, 10, 0), '192.168.0.5')

        # Get statistics for January 2022
        monthly_stats = (self.tracker.get_stats_by_resolution(
            datetime(2022, 1, 1),
            datetime(2022, 2, 1),
            'day'))
        self.assertEqual(3, len(monthly_stats))

        # Check the statistics for each day
        self.assertEqual(1, monthly_stats[0][1])
        self.assertEqual(1, monthly_stats[0][2])
        self.assertEqual(2, monthly_stats[1][1])
        self.assertEqual(2, monthly_stats[1][2])
        self.assertEqual(2, monthly_stats[2][1])
        self.assertEqual(1, monthly_stats[2][2])

    def test_get_stats_by_months(self):
        # Simulate multiple visits in different months
        self.tracker.update(datetime(2022, 1, 1, 13, 15), '192.168.0.1')
        self.tracker.update(datetime(2022, 1, 2, 14, 2), '192.168.0.2')
        self.tracker.update(datetime(2022, 2, 1, 10, 0), '192.168.0.3')
        self.tracker.update(datetime(2022, 3, 5, 12, 30), '192.168.0.4')
        self.tracker.update(datetime(2022, 3, 15, 16, 45), '192.168.0.4')
        self.tracker.update(datetime(2023, 2, 15, 16, 45), '192.168.0.5')

        # Get statistics for the year 2022
        monthly_stats = self.tracker.get_stats_by_resolution(
            datetime(2022, 1, 1),
            datetime(2023, 1, 1),
            'month')
        self.assertEqual(3, len(monthly_stats))

        # Check the statistics for each month
        self.assertEqual(2, monthly_stats[0][1])
        self.assertEqual(2, monthly_stats[0][2])
        self.assertEqual(1, monthly_stats[1][1])
        self.assertEqual(1, monthly_stats[1][2])
        self.assertEqual(2, monthly_stats[2][1])
        self.assertEqual(1, monthly_stats[2][2])

    def test_get_stats_by_wrong_resolution(self):
        # The gap of a decade is not supported
        with self.assertRaises(ValueError):
            self.tracker.get_stats_by_resolution(datetime(2022, 1, 1),
                                                 datetime(2022, 1, 31),
                                                 'decade')

    def test_get_weekdays_stats(self):
        # Simulate multiple visits in different weekdays
        self.tracker.update(datetime(2022, 1, 3), '192.168.0.1')  # Monday
        self.tracker.update(datetime(2022, 1, 10), '192.168.0.2')  # Monday
        self.tracker.update(datetime(2022, 1, 4), '192.168.0.3')  # Tuesday
        self.tracker.update(datetime(2022, 1, 11), '192.168.0.3')  # Tuesday
        self.tracker.update(datetime(2022, 1, 5), '192.168.0.4')  # Wednesday

        weekday_stats = self.tracker.get_weekdays_stats(
            datetime(2022, 1, 1),
            datetime(2022, 1, 31))
        self.assertEqual(3, len(weekday_stats))

        for weekday, total, unique in weekday_stats:
            match weekday:
                case 'Monday':
                    self.assertEqual(2, total)
                    self.assertEqual(2, unique)
                case 'Tuesday':
                    self.assertEqual(2, total)
                    self.assertEqual(1, unique)
                case 'Wednesday':
                    self.assertEqual(1, total)
                    self.assertEqual(1, unique)
