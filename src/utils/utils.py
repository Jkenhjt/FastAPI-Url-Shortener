import time


def generate_url() -> str:
    s_url: str = str(hex(int(time.time_ns())))
    return s_url[2:]
