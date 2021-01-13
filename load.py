import datetime as dt
import time
import math

i = 0
j = 0
j_max = 1e6
t_start = time.time()
while True:
    while j < j_max:
        j += 1
        y = (math.sin(math.sqrt(j))**3 / math.cos(math.sqrt(j))**4 * math.tan(math.sqrt(j))**5)**3
    i += 1
    j = 0
    s = dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    t = '{:.2f}'.format((time.time() - t_start) / 60)+ " min"
    print(str(i) + " - " + s + " - "  + t + " val = " + str(y))
#     time.sleep(2)
    
