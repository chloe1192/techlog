from datetime import datetime


def parse_datetime(date_str, time_str):
    """
    Returns a datetime or None.
    """
    if not date_str or not time_str:
        return None

    try:
        return datetime.strptime(
            f"{date_str} {time_str}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return None