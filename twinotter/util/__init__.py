import datetime


def round_datetime(time, resolution, type=None):
    """Round the time by resolution

    Args:
        time (datetime.datetime | datetime.timedelta):
        resolution (datetime.timedelta):
        type (): Round up or down (ceil or floor)

    Returns:
        datetime.datetime
    """
    try:
        excess = time % resolution
    except TypeError:
        excess = datetime.timedelta(
            days=time.day,
            hours=time.hour,
            minutes=time.minute,
            seconds=time.second,
            microseconds=time.microsecond
        ) % resolution

    if type == 'ceil' or (excess > resolution / 2 and type != 'floor'):
        # Round up
        return time - excess + resolution
    else:
        # Round down
        return time - excess
