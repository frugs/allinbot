import unittest
import datetime

from allinbot.calendar import calendarutils


class CalendarTestCase(unittest.TestCase):

    def setUp(self):
        self.five_hours = datetime.timedelta(hours=5)
        self.two_hours_thirty_minutes = datetime.timedelta(hours=2, minutes=30)
        self.fifty_seconds = datetime.timedelta(seconds=50)

    def test_describe_five_hours_in_hours(self):
        description = calendarutils.describe_time_delta(self.five_hours, hours=True)
        self.assertEqual("5 hour(s)", description)

    def test_describe_five_hours_in_minutes(self):
        description = calendarutils.describe_time_delta(self.five_hours, minutes=True)
        self.assertEqual("300 minute(s)", description)

    def test_describe_two_hours_thirty_minutes_in_hours(self):
        description = calendarutils.describe_time_delta(self.two_hours_thirty_minutes, hours=True)
        self.assertEqual("3 hour(s)", description)

    def test_describe_two_hours_thirty_minutes_in_hours_and_minutes(self):
        description = calendarutils.describe_time_delta(self.two_hours_thirty_minutes, hours=True, minutes=True)
        self.assertEqual("2 hour(s) 30 minute(s)", description)

    def test_describe_two_hours_thirty_minutes_in_hours_and_minutes_and_seconds(self):
        description = calendarutils.describe_time_delta(self.two_hours_thirty_minutes, hours=True, minutes=True, seconds=True)
        self.assertEqual("2 hour(s) 30 minute(s)", description)

    def test_describe_fifty_seconds_in_hours_and_seconds(self):
        description = calendarutils.describe_time_delta(self.fifty_seconds, hours=True, seconds=True)
        self.assertEqual("50 second(s)", description)

    def test_describe_fifty_seconds_seconds(self):
        description = calendarutils.describe_time_delta(self.fifty_seconds, seconds=True)
        self.assertEqual(description, "50 second(s)")




