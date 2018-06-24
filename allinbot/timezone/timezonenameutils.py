import pytz


def localise_to_possible_timezones_from_name(naive_datetime, timezone_name):
    tz_name_dict = {}
    for tz_str in pytz.common_timezones:
        tz = pytz.timezone(tz_str)
        localised_datetime = tz.localize(naive_datetime)
        if localised_datetime.tzname() == timezone_name:
            tz_name_dict[localised_datetime.strftime(
                "%z")] = localised_datetime

    return list(tz_name_dict.values())


def normalise_to_possible_timezones_from_name(localised_datetime,
                                              timezone_name):
    tz_name_dict = {}
    for tz_str in pytz.common_timezones:
        tz = pytz.timezone(tz_str)
        normalised_datetime = tz.normalize(localised_datetime)
        if normalised_datetime.tzname() == timezone_name:
            tz_name_dict[normalised_datetime.strftime(
                "%z")] = normalised_datetime

    return list(tz_name_dict.values())
