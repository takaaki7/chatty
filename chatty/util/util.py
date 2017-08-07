def td2hm(timedelta):
    return timedelta.seconds // 3600, (timedelta.seconds // 60) % 60
