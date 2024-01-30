import calendar
from datetime import datetime
from sqlalchemy import create_engine, func, between
from sqlalchemy.orm import sessionmaker
from database.visit_model import Base, Visit


class VisitTracker:
    def __init__(self, db_path="sqlite:///database/visits.db"):
        engine = create_engine(db_path, echo=True)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def update(self, date: datetime, ip):
        self.session.add(Visit(date=date, ip=ip))
        self.session.commit()

    def get_daily_total(self, date: datetime):
        return (self.session.query(func.count(Visit.date))
                .filter(func.DATE(Visit.date) == date.date())
                .scalar())

    def get_monthly_total(self, date: datetime):
        year = func.extract('year', Visit.date)
        month = func.extract('month', Visit.date)
        return (self.session.query(func.count(Visit.date))
                .filter(year == date.year, month == date.month)
                .scalar())

    def get_yearly_total(self, date: datetime):
        return (self.session.query(func.count(Visit.date))
                .filter(func.extract('year', Visit.date) == date.year)
                .scalar())

    def get_total_count(self):
        return (self.session.query(func.count(Visit.date))
                .scalar())

    def get_day_unique(self, date: datetime):
        year = func.extract('year', Visit.date)
        month = func.extract('month', Visit.date)
        day = func.extract('day', Visit.date)
        return (self.session.query(func.count(func.distinct(Visit.ip)))
                .filter(year == date.year,
                        month == date.month,
                        day == date.day)
                .scalar())

    def get_month_unique(self, date: datetime):
        year = func.extract('year', Visit.date)
        month = func.extract('month', Visit.date)
        return (self.session.query(func.count(func.distinct(Visit.ip)))
                .filter(year == date.year, month == date.month)
                .scalar())

    def get_yearly_unique(self, date: datetime):
        year = func.extract('year', Visit.date)
        return (self.session.query(func.count(func.distinct(Visit.ip)))
                .filter(year == date.year)
                .scalar())

    def get_unique_count(self):
        return (self.session.query(func.count(func.distinct(Visit.ip)))
                .scalar())

    def get_total_on_range(self, start_date: datetime, end_date: datetime):
        return (self.session.query(func.count(Visit.date))
                .filter(between(Visit.date, start_date, end_date))
                .scalar())

    def get_unique_on_range(self, start_date: datetime, end_date: datetime):
        return (self.session.query(func.count(func.distinct(Visit.ip)))
                .filter(between(Visit.date, start_date, end_date))
                .scalar())

    def get_stats_by_resolution(self, start_date: datetime, end_date: datetime,
                                resolution_range: str):
        if resolution_range not in ['year', 'month', 'day', 'hour', 'minute',
                                    'second']:
            raise ValueError('Choose a valid resolution range from datetime '
                             'attributes')
        resolution = func.extract(resolution_range, Visit.date)
        visits = (self.session.query(Visit.date, resolution,
                                     func.count().label('total_visits'),
                                     func.count(func.distinct(Visit.ip))
                                     .label('unique_visitors'))
                  .filter(between(Visit.date, start_date, end_date))
                  .group_by(resolution)
                  .all())
        stats = []
        for visit in visits:
            date = (visit[0], visit[1])
            total_visits = visit[2]
            unique_visitors = visit[3]
            stats.append((date, total_visits, unique_visitors))
        return stats

    def get_weekdays_stats(self, start_date: datetime, end_date: datetime):
        visits = (self.session.query(func.extract('dow', Visit.date),
                                     func.count().label('total_visits'),
                                     func.count(func.distinct(Visit.ip))
                                     .label('unique_visitors'))
                  .filter(between(Visit.date, start_date, end_date))
                  .group_by(func.extract('dow', Visit.date))
                  .all())
        weekday_stats = []
        for visit in visits:
            weekday_name = calendar.day_name[visit[0] - 1]
            total_visits = visit[1]
            unique_visitors = visit[2]
            weekday_stats.append((weekday_name, total_visits, unique_visitors))
        return weekday_stats
