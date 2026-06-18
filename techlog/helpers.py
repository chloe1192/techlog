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
    
def parse_date(date_str):    
    """
    Returns a datetime or None.
    """
    if not date_str:
        return None

    try:
        return datetime.strptime(
            f"{date_str}",
            "%Y-%m-%d"
        )
    
    except ValueError:
        return None

def loop_trough_fluids(post, tanks, *args):
    return_dict = {}
    
    for tank in tanks:
        return_dict[tank.id] = {}
        for arg in args:
            key = f"{arg}{tank.id}"
            return_dict[tank.id][arg] = post[key]

    return return_dict