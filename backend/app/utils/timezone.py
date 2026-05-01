from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))


def get_beijing_time():
    return datetime.now(CST)


def to_beijing_time(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(CST)
