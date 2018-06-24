import datetime

_SECONDS_IN_MINUTE = 60
_SECONDS_IN_HOUR = 60 * _SECONDS_IN_MINUTE
_SECONDS_IN_DAY = 24 * _SECONDS_IN_HOUR


def describe_time_delta(time_delta: datetime.timedelta,
                        days: bool = False,
                        hours: bool = False,
                        minutes: bool = False,
                        seconds: bool = False):

    remaining_seconds = int(time_delta.total_seconds())

    description_components = []

    if days:
        num_days, remaining_seconds = divmod(remaining_seconds,
                                             _SECONDS_IN_DAY)
        # round up if there is a lower granularity component we're not displaying
        num_days += 1 if remaining_seconds and not (hours or minutes
                                                    or seconds) else 0
        if num_days:
            description_components.append("{} day(s)".format(num_days))

    if hours:
        num_hours, remaining_seconds = divmod(remaining_seconds,
                                              _SECONDS_IN_HOUR)
        # round up if there is a lower granularity component we're not displaying
        num_hours += 1 if remaining_seconds and not (minutes or seconds) else 0
        if num_hours:
            description_components.append("{} hour(s)".format(num_hours))

    if minutes:
        num_minutes, remaining_seconds = divmod(remaining_seconds,
                                                _SECONDS_IN_MINUTE)
        # round up if there is a lower granularity component we're not displaying
        num_minutes += 1 if remaining_seconds and not seconds else 0
        if num_minutes:
            description_components.append("{} minute(s)".format(num_minutes))

    if seconds:
        num_seconds = int(remaining_seconds)
        if num_seconds:
            description_components.append("{} second(s)".format(num_seconds))

    return " ".join(description_components)
