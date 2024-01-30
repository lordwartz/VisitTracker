from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Visit(Base):
    __tablename__ = 'visits'

    date = Column('date', DateTime, primary_key=True)
    ip = Column("ip", String)

    def __init__(self, date: datetime, ip: str):
        self.ip = ip
        self.date = date

    def __repr__(self):
        return f"<Visit date: {self.date}, ip: {self.ip}>"
