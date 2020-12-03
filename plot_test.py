import time
import datetime

import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
from matplotlib import style

from lib.mysql_amod_lib import Mysql_amod
mysql_amod = Mysql_amod('192.168.1.139')
sql_txt = "SELECT time_stamp, mes_value FROM tlog;"
data = mysql_amod.get_data(sql_txt)

mes_time = []
mes_tension = []

for row in data:
    mes_time.append(row[0])
    mes_tension.append(row[1])

# Convert datetime.datetime to float days since 0001-01-01 UTC.
dates = [mdates.date2num(t) for t in mes_time]

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.set_title("first plot test")

# Configure x-ticks
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M'))

# Plot temperature data on left Y axis
ax1.set_ylabel("Tension [V]")
ax1.plot_date(dates, mes_tension, '-', label="Tension accu", color='b')
# ax1.plot_date(dates, mes_time, '-', label="Feels like", color='b')

# Format the x-axis for dates (label formatting, rotation)
fig.autofmt_xdate(rotation=60)
fig.tight_layout()

# Show grids and legends
ax1.grid(True)
ax1.legend(loc='best', framealpha=0.5)
plt.show()
plt.savefig("figure.png")








# 
# # conn = sqlite3.connect('tutorial.db')
# c = conn.cursor()
# wordUsed = 'Python Sentiment'
# sql = "SELECT time_ FROM tlog;"
# 
# graphArray = []
# 
# 
# 
# for row in c.execute(sql, [(wordUsed)]):
#     startingInfo = str(row).replace(')','').replace('(','').replace('u\'','').replace("'","")
#     splitInfo = startingInfo.split(',')
#     graphArrayAppend = splitInfo[2]+','+splitInfo[4]
#     graphArray.append(graphArrayAppend)
# 
# datestamp, value = np.loadtxt(graphArray,delimiter=',', unpack=True,
#                               converters={ 0: mdates.strpdate2num(' %Y-%m-%d %H:%M:%S')})
# 
# fig = plt.figure()
# 
# rect = fig.patch
# 
# ax1 = fig.add_subplot(1,1,1, axisbg='white')
# plt.plot_date(x=datestamp, y=value, fmt='b-', label = 'value', linewidth=2)
# plt.show()   
