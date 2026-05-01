from datetime import datetime


def get_beijing_time():
    # 直接使用本地时间
    return datetime.now()


def to_beijing_time(dt):
    # 直接返回本地时间，不做时区转换
    return dt


def format_datetime(dt):
    if dt is None:
        return None
    dt_obj = to_beijing_time(dt)
    if dt_obj is None:
        return None
    return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
