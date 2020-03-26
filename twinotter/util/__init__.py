import datetime


def round_datetime(time, resolution):
    """Round the time by resolution (floor rounding)

    Args:
        time (datetime.datetime):
        resolution (datetime.timedelta):

    Returns:
        datetime.datetime
    """
    excess = datetime.timedelta(
        days=time.day,
        hours=time.hour,
        minutes=time.minute,
        seconds=time.second,
        microseconds=time.microsecond
    ) % resolution

    return time - excess
