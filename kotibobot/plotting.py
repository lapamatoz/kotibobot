# - *- coding: utf- 8 - *-
import time
from datetime import datetime, timedelta
# packages for time series
#import dateutil.parser
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
#from matplotlib import pyplot
import matplotlib
import matplotlib.dates as mdates # helps to format dates in x-axis
import math
import multiprocessing as mp # asychronous plotting

from house import *
from common_functions import *

matplotlib.use('svg') # no GUI when plotting

# asychronous plotting https://gist.github.com/astrofrog
class AsyncPlotter:
    def __init__(self, processes=mp.cpu_count()): #
        self.manager = mp.Manager()
        self.nc = self.manager.Value("i", 0)
        self.pids = []
        self.processes = processes
    def async_plotter(self, nc, fig, filename, processes):
        while nc.value >= processes:
            time.sleep(0.05)
        nc.value += 1
        #print("Plotting " + filename)
        fig.savefig(filename)
        plt.close(fig)
        nc.value -= 1
    def save(self, fig, filename):
        p = mp.Process(
            target=self.async_plotter, args=(self.nc, fig, filename, self.processes)
        )
        p.start()
        self.pids.append(p)
    def join(self):
        for p in self.pids:
            p.join()

### TIME SERIES PLOTTING ###

def load_ts_data():
  file_name = '/home/lowpaw/Downloads/kotibobot/' + datetime.today().strftime("%Y-%m") + '.pkl'
  return pd.read_pickle(file_name)

def temp_48_all_rooms(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'temp_allrooms.svg'
  plotname = "Temperature, 48h all rooms"
  if not make_plot:
    return html_link(plotname, filename)
  
  data = data_orig
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  # min and max temps are used to filter
  # too low and too high outside temp -values
  max_room_temp = -float('inf')
  min_room_temp =  float('inf')
  
  temps = []
  for room in rooms:
    for sensor in mi_in_rooms[room]:
      temps.append(sensor + " temp")
      max_room_temp = max(max_room_temp, data[sensor + " temp"].max())
      min_room_temp = min(min_room_temp, data[sensor + " temp"].min())
      
  max_room_temp = max_room_temp + 5
  min_room_temp = min_room_temp - 5
  
  # we filter too low and
  # too high outside temp -values
  data['outside temp'] = data['outside temp'].where(data['outside temp'] < max_room_temp, float('nan'))
  data['outside temp'] = data['outside temp'].where(data['outside temp'] > min_room_temp, float('nan'))
  
  fig, ax = plt.subplots(1,1,figsize=(11,9))
  #ax = data.plot(x="time",y=(temps), alpha=0.7)
  data.plot(x="time",y=(temps), alpha=0.7, ax=ax)
  data.plot(x="time",y="outside temp", alpha=0.7, ax=ax, linestyle='dashed')
  plt.ylabel('    °C',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  ax.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax.yaxis.grid(True, which='major', alpha = 0.2)
  ax.yaxis.grid(True, which='minor')
  ax.xaxis.grid(True, alpha=0.2)
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  plt.xticks(rotation=0, ha='center')
  ax.xaxis.set_major_formatter(myFmt)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  
  #plt.show()
  
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def humidity_48_all_rooms(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'humidity_allrooms.svg'
  plotname = "Humidity, 48h all rooms"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  humidities = []
  for sensor in mis:
    humidities.append(mac_to_name[sensor] + " humidity")
  
  fig, ax = plt.subplots(1,1,figsize=(11,9))
  data.plot(x="time",y=(humidities), ax=ax, alpha=0.7) # ax=ax laittaa samaan kuvaan
  data.plot(x="time",y="outside humidity", ax=ax, alpha=0.7, linestyle='dashed')
  
  plt.ylim([-2, 102])
  
  plt.ylabel('%',rotation=0)
  ax.set_xlabel('')
  ax.xaxis.grid(True, alpha=0.2)
  ax.yaxis.grid(True, alpha=0.2)
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  plt.xticks(rotation=0, ha='center')
  ax.xaxis.set_major_formatter(myFmt)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def temp_48(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_target_temp.svg'
  plotname = "Temperature, 48h"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  valves = []
  for eq3 in eq3_in_rooms[room]:
    valves.append(eq3 + " valve")
  
  targets = []
  for eq3 in eq3_in_rooms[room]:
    targets.append(eq3 + " target")
      
  temps = []
  for sensor in mi_in_rooms[room]:
    temps.append(sensor + " temp")
  
  fig, ax1 = plt.subplots(1,1,figsize=(11,9))
  
  data.plot(x="time",y=(temps), alpha=0.7, color='r', ax=ax1)
  data.plot(x="time",y=(targets), alpha=0.7,linestyle='dashed', ax=ax1)
  plt.ylabel('°C   ',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  plt.xticks(rotation=0, ha='center')
  
  ax2 = ax1.twinx()
  data.plot(x="time",y=(valves),linestyle=':', ax=ax2, alpha=0.7) # ax=ax laittaa samaan kuvaan secondary_y=True,
  #plt.ylim([-2, 102])
  #ax1.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax1.yaxis.grid(True, which='major', alpha = 0.2)
  ax1.yaxis.grid(True, which='minor')
  ax1.xaxis.grid(True, alpha=0.2)
  plt.ylabel('%',rotation=0)
  ax1.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  #plt.xticks(rotation=0, ha='center', ax=ax1) ###########
  #ax1.set_xticklabels(rotation=0, ha='center', ax=ax1) ###########
  ax1.xaxis.set_major_formatter(myFmt)
  #plt.show()
  
  
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def temp_offset(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_offset.svg'
  plotname = "Error, 48h"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  valves = []
  for eq3 in eq3_in_rooms[room]:
    valves.append(eq3 + " valve")
      
  offsets = []
  for eq3 in eq3_in_rooms[room]:
    offsets.append(eq3 + " offset")
  
  targets = []
  for eq3 in eq3_in_rooms[room]:
    targets.append(eq3 + " target")
      
  temps = []
  for sensor in mi_in_rooms[room]:
    temps.append(sensor + " temp")
  
  data['temp'] =   data[temps].mean(axis = 1,skipna = True)
  data['target'] = data[targets].mean(axis = 1,skipna = True)
  data['error'] = data['temp'].subtract(data['target'])
  #offsets.append('error')
  
  fig, ax1 = plt.subplots(1,1,figsize=(11,9))
  data.plot(x="time",y='error', alpha=0.7, color = 'm', ax=ax1)
  data.plot(x="time",y=offsets, linestyle='dashed', alpha=0.7, ax=ax1)
  plt.ylabel('°C   ',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  plt.xticks(rotation=0, ha='center')
  
  ax2 = ax1.twinx()
  
  data.plot(x="time",y=valves,ax=ax2,linestyle=':', alpha=0.7) # ax=ax laittaa samaan kuvaan
  plt.ylabel('%',rotation=0)
  ax1.set_xlabel('')
  plt.ylim([-2, 102])
  ax1.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  ax1.set_yticks([0.0001], minor=True)
  
  ax1.yaxis.grid(True, which='major', alpha = 0.2)
  ax1.yaxis.grid(True, which='minor')
  ax1.xaxis.grid(True, alpha=0.2)
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  
  ax1.xaxis.set_major_formatter(myFmt)
  
  #plt.show()
  
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)


def temp_days(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_temp.svg'
  plotname = "Temperature, past three days"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t2 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  t3 = t2 + timedelta(hours = 24)
  t1 = t2 - timedelta(hours = 24)
  t0 = t2 - timedelta(hours = 48)
  
  data0 = data[data['time'] > t0]
  data0 = data0[data0['time'] < t1]
  data0['time'] = data0['time'] + timedelta(hours = 48)
  
  data1 = data[data['time'] > t1]
  data1 = data1[data1['time'] < t2]
  data1['time'] = data1['time'] + timedelta(hours = 24)
  
  data2 = data[data['time'] > t2]
  data2 = data2[data2['time'] < t3]
      
  temps = []
  for sensor in mi_in_rooms[room]:
    temps.append(sensor + " temp")
  temp = temps[0] # mean could be calculated, if many sensors
  
  fig, ax = plt.subplots(1,1,figsize=(11,9))
  data2.plot(x="time",y=temp,color='r', alpha=0.8, ax=ax)
  data1.plot(x="time",y=temp,linestyle='dashed',ax=ax,color='r', alpha=0.7) # ax=ax laittaa samaan kuvaan
  data0.plot(x="time",y=temp,linestyle=':',ax=ax,color='r', alpha=0.6) # ax=ax laittaa samaan kuvaan
  plt.ylabel('    °C',rotation=0)
  ax.set_xlabel('')
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  ax.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  ax.yaxis.grid(True, which='major', alpha = 0.2)
  ax.xaxis.grid(True, alpha=0.2)
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  plt.xticks(rotation=0, ha='center')
  
  #plt.show()
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  #subprocess.run(['cp', '/home/lowpaw/Downloads/kotibobot/' + filename, '/var/www/html/kotibobot/'])
  return html_link(plotname, filename)
  
def humidity_days(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_humidity.svg'
  plotname = "Humidity, past three days"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t2 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  t3 = t2 + timedelta(hours = 24)
  t1 = t2 - timedelta(hours = 24)
  t0 = t2 - timedelta(hours = 48)
  
  data0 = data[data['time'] > t0]
  data0 = data0[data0['time'] < t1]
  data0['time'] = data0['time'] + timedelta(hours = 48)
  
  data1 = data[data['time'] > t1]
  data1 = data1[data1['time'] < t2]
  data1['time'] = data1['time'] + timedelta(hours = 24)
  
  data2 = data[data['time'] > t2]
  data2 = data2[data2['time'] < t3]
  
  humidities = []
  for sensor in mi_in_rooms[room]:
    humidities.append(sensor + " humidity")
  humidity = humidities[0] # mean could be calculated, if many sensors
  
  fig, ax = plt.subplots(1,1,figsize=(11,9))
  data2.plot(x="time",y=humidity,color='b',alpha=0.8, ax=ax)
  plt.ylim([-2, 102])
  plt.ylabel(' %',rotation=0)
  
  data1.plot(x="time",y=humidity,linestyle='dashed',ax=ax,color='b',alpha=0.7) # ax=ax laittaa samaan kuvaan
  data0.plot(x="time",y=humidity,linestyle=':',ax=ax,color='b',alpha=0.6) # ax=ax laittaa samaan kuvaan
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.xaxis.grid(True, alpha=0.2)
  ax.yaxis.grid(True, alpha=0.2)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  plt.xticks(rotation=0, ha='center')
  
  #plt.show()
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

#plot_ts(['työkkäri']) # , '2021-05-08T16:15', '2021-05-10T17:10'

def html_link(text,url):
  return "<a href='https://cloud.laurijokinen.com/kotibobot/" + url + "'>" + text +"</a>"

def main_function(draw_plots = True):
  data_orig = load_ts_data()
  
  a = AsyncPlotter()
  res = ["Kaikki huoneet"] # in html
  res.append(temp_48_all_rooms(data_orig,a,draw_plots))
  res.append(humidity_48_all_rooms(data_orig,a,draw_plots))
  for room in rooms:
    res.append("\n" + room.capitalize())
    res.append(temp_48(room, data_orig,a,draw_plots))
    res.append(temp_offset(room, data_orig,a,draw_plots))
    res.append(temp_days(room, data_orig,a,draw_plots))
    res.append(humidity_days(room, data_orig,a,draw_plots))
  a.join()
  plt.close('all')
  
  return "\n".join(res)

def latest_data():
  data = load_ts_data()
  index = len(data.index)-1
  cols = data.columns.values.tolist()
  timeformat = '%-d.%-m. klo %-H:%M'
  
  res = ['Latest measurement at ' + str(data.iloc[index]['time'].strftime(timeformat)) + '\n']
  for col in cols:
    if not col == 'time':
      if not math.isnan(data.iloc[-1][col]):
        res.append(col + ' : ' + str(data.iloc[-1][col]))
      else:
        index = len(data.index)-1
        while index > 0 and math.isnan(data.iloc[index][col]):
          index = index - 1
        res.append(col + ' : ' + str(data.iloc[index][col]) + ' (timestamp: ' + str(data.iloc[index]['time'].strftime(timeformat)) + ')')
  res.sort()
  return '\n'.join(res)