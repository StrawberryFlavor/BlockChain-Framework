# -*- coding: utf-8 -*-

import time
import datetime


def get_nowtime_unix():
    dtime = datetime.datetime.now()
    ans_time = time.mktime(dtime.timetuple())
    now_unix = int(ans_time)
    return now_unix

