import time, datetime

time1 = datetime.datetime.now()
time.sleep(5)
time2 = datetime.datetime.now()

time_diff = time.mktime(time2.timetuple()) - time.mktime(time1.timetuple())
print(time_diff)