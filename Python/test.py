import datetime

i = 0
start = datetime.datetime.now()
last = start

while True:
    #my_function()
    i += 1
    now = datetime.datetime.now()
    if now - last > datetime.timedelta(seconds=10):
        last = now
        print('Elapsed: ' + str(now-start) + ' | Iteration #' + str(i))