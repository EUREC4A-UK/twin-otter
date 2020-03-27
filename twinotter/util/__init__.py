import datetime


def round_datetime(time, resolution):
    """Round the time by resolution

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

    if excess > resolution / 2:
        # Round up
        return time - excess + resolution
    else:
        # Round down
        return time - excess
