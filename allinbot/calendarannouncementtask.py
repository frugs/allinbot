import datetime
import urllib.request
import icalendar
import dateutil.rrule
import discord
import pytz

from .task import Task
from .calendar import calendarutils

_ANNOUNCEMENT_CHANNEL_ID = "195057719487627264"
_ANNOUNCEMENT_TAG = "@here"
_CALENDAR_URL = "https://calendar.google.com/calendar/ical/3om5b2vfubpugkf3vr6fahh01k%40group.calendar.google.com/public/basic.ics"
_TIME_FORMAT = "%H:%M %d %b %Y %Z%z"
_FIVE_DAY_ANNOUNCMENT_INTERVAL = datetime.timedelta(days=1)


class CalendarAnnouncementTask(Task):

    def __init__(self):
        self._five_minute_announced_events = {}
        self._thirty_minute_announced_events = {}
        self._last_five_day_announcement = datetime.datetime.fromtimestamp(0, datetime.timezone.utc)

    async def perform_task(self, client: discord.Client):
        event_loop = client.loop

        response = await event_loop.run_in_executor(None, urllib.request.urlopen, _CALENDAR_URL)
        calendar_bytes = await event_loop.run_in_executor(None, response.read)
        calendar = await event_loop.run_in_executor(None, icalendar.Calendar.from_ical, calendar_bytes)

        calendar_timezone_name = calendar["X-WR-TIMEZONE"]
        calendar_timezone = pytz.timezone(calendar_timezone_name)

        now = datetime.datetime.now(datetime.timezone.utc)

        five_days_time = now + datetime.timedelta(days=5)
        thirty_minutes_time = now + datetime.timedelta(minutes=30)
        five_minutes_time = now + datetime.timedelta(minutes=5)

        unannounced_events_in_next_five_minutes = []
        unannounced_events_in_next_thirty_minutes = []
        events_in_next_5_days = []

        for component in calendar.walk():
            if component.name == icalendar.Event.name:
                start_time = icalendar.vDDDTypes.from_ical(component["DTSTART"])

                # DTSTART can be a datetime.date if the event is an all-day event
                if isinstance(start_time, datetime.date) and not isinstance(start_time, datetime.datetime):
                    start_time = datetime.datetime.combine(start_time, datetime.time())
                    start_time = calendar_timezone.localize(start_time)

                if start_time < now and "RRULE" in component:
                    parsed_rrule = dateutil.rrule.rrulestr(component["RRULE"].to_ical().decode(), dtstart=start_time)
                    start_time = parsed_rrule.after(now)

                # there may be no more valid start times for recurring events after the present time
                if not start_time:
                    continue

                event = (start_time, component)

                if now < start_time <= five_minutes_time and component["UID"] not in self._five_minute_announced_events:
                    unannounced_events_in_next_five_minutes.append(event)

                elif five_minutes_time < start_time <= thirty_minutes_time and component["UID"] not in self._thirty_minute_announced_events:
                    unannounced_events_in_next_thirty_minutes.append(event)

                elif thirty_minutes_time < start_time <= five_days_time:
                    events_in_next_5_days.append(event)

        # only make an announcement if we have an unannounced event coming up in the next thirty minutes or in the
        # next 5 mins
        if unannounced_events_in_next_five_minutes or unannounced_events_in_next_thirty_minutes:

            unannounced_events_in_next_five_minutes.sort(key=lambda x:x[0])
            unannounced_events_in_next_thirty_minutes.sort(key=lambda x: x[0])
            events_in_next_5_days.sort(key=lambda x: x[0])

            messages_to_send = [_ANNOUNCEMENT_TAG]
            if unannounced_events_in_next_five_minutes:
                five_minute_reminder_message = "__Events starting in the next five minutes:__\n"

                for start_time, event in unannounced_events_in_next_five_minutes:
                    start_time_string = calendar_timezone.normalize(start_time).strftime(_TIME_FORMAT)
                    time_delta_string = calendarutils.describe_time_delta(start_time - now, minutes=True)

                    five_minute_reminder_message += "In {} - **{}**\n*{}*\n".format(
                        time_delta_string, event["SUMMARY"], start_time_string)
                    self._five_minute_announced_events[event["UID"]] = start_time

                messages_to_send.append(five_minute_reminder_message)

            if unannounced_events_in_next_thirty_minutes:
                thirty_minute_reminder_message = "__Events starting in the next thirty minutes:__\n"

                for start_time, event in unannounced_events_in_next_thirty_minutes:
                    start_time_string = calendar_timezone.normalize(start_time).strftime(_TIME_FORMAT)
                    time_delta_string = calendarutils.describe_time_delta(start_time - now, minutes=True)

                    thirty_minute_reminder_message += "In {} - **{}**\n*{}*\n".format(
                        time_delta_string, event["SUMMARY"], start_time_string)
                    self._thirty_minute_announced_events[event["UID"]] = start_time

                messages_to_send.append(thirty_minute_reminder_message)

            if events_in_next_5_days and now - self._last_five_day_announcement > _FIVE_DAY_ANNOUNCMENT_INTERVAL:
                self._last_five_day_announcement = now
                
                announcement_message = "__Upcoming events in the next 5 days:__\n"

                for start_time, event in events_in_next_5_days:
                    start_time_string = calendar_timezone.normalize(start_time).strftime(_TIME_FORMAT)
                    time_delta_string = calendarutils.describe_time_delta(start_time - now, days=True, hours=True)

                    announcement_message += "In {} - **{}**\n *{}*\n\n".format(
                        time_delta_string, event["SUMMARY"], start_time_string)

                messages_to_send.append(announcement_message)

            if client.is_logged_in and not client.is_closed:
                channel = client.get_channel(_ANNOUNCEMENT_CHANNEL_ID)
                await client.send_message(channel, "\n".join(messages_to_send))

            self._five_minute_announced_events = dict(filter(lambda x: x[1] >= now, self._five_minute_announced_events.items()))
            self._thirty_minute_announced_events = dict(filter(lambda x: x[1] >= now, self._thirty_minute_announced_events.items()))
