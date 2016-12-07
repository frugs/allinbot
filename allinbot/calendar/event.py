import datetime


class CalendarEvent:

    def __init__(self, event_id: str, start_time: datetime.datetime, summary: str):
        self._event_id = event_id
        self._start_time = start_time
        self._event_summary = summary

    def event_id(self):
        return self._event_id

    def start_time(self):
        return self._start_time

    def summary(self):
        return self._event_summary
