from datetime import datetime


def get_beijing_time():
    # 直接使用本地时间
    return datetime.now()


def to_beijing_time(dt):
    # 直接返回本地时间，不做时区转换
    return dt
