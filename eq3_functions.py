# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash
import time
from datetime import datetime

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

rooms = json.loads("{}")

rooms["olkkari"] = json.loads("{}")
rooms["olkkari"]["eq3"] = [koodit["keittiön nuppi"], koodit["olkkarin nuppi"]]
rooms["olkkari"]["mi"] = [koodit["olkkarin lämpömittari"]]

rooms["makkari"] = json.loads("{}")
rooms["makkari"]["eq3"] = [koodit["makkarin nuppi"]]
rooms["makkari"]["mi"] = [koodit["makkarin lämpömittari"]]

rooms["työkkäri"] = json.loads("{}")
rooms["työkkäri"]["eq3"] = [koodit["työkkärin nuppi"]]
rooms["työkkäri"]["mi"] = [koodit["työkkärin lämpömittari"]]


mac_to_name = json.loads("{}")
mac_to_name[koodit["keittiön nuppi"]] = "keittiön nuppi"
mac_to_name[koodit["olkkarin nuppi"]] = "olkkarin nuppi"
mac_to_name[koodit["makkarin nuppi"]] = "makkarin nuppi"
mac_to_name[koodit["työkkärin nuppi"]] = "työkkärin nuppi"
mac_to_name[koodit["työkkärin lämpömittari"]] = "työkkärin lämpömittari"
mac_to_name[koodit["makkarin lämpömittari"]] = "makkarin lämpömittari"
mac_to_name[koodit["olkkarin lämpömittari"]] = "olkkarin lämpömittari"

# kokeillaan gittiä :)

name_to_mac = json.loads("{}")
for mac in mac_to_name:
  name_to_mac[mac_to_name[mac]] = mac

# Create an array with all eq-3 devices (MAC)
eq3s = []
for room in rooms:
  if "eq3" in rooms[room]:
    for eq3 in rooms[room]["eq3"]:
      eq3s.append(eq3)

# Create an array with all mi devices (MAC)
mis = []
for room in rooms:
  if "mi" in rooms[room]:
    for mi in rooms[room]["mi"]:
      mis.append(mi)

# eq3s in rooms
eq3_in_rooms = json.loads("{}")
for room in rooms:
  eq3_in_rooms[room] = []
  if "eq3" in rooms[room]:
    for eq3 in rooms[room]["eq3"]:
      eq3_in_rooms[room].append(mac_to_name[eq3])


# mi in rooms
mi_in_rooms = json.loads("{}")
for room in rooms:
  mi_in_rooms[room] = []
  if "mi" in rooms[room]:
    for mi in rooms[room]["mi"]:
      mi_in_rooms[room].append(mac_to_name[mi])

#### FUNCTIONS

def replace_macs_to_names(str):
  for mac in mac_to_name:
    str = str.replace(mac, mac_to_name[mac])
  return str

def eq3_command(str):
  s = ['/home/lowpaw/Downloads/eq3/eq3.exp', 'hci1'] + str.split(' ')
  res = subprocess.run(s, stdout=subprocess.PIPE)
  res_str = res.stdout.decode('utf-8')
  if "Connection failed" in res_str or "ERROR" in res_str:
    print('Yhteys pätki kerran')
    time.sleep(5)
    res = subprocess.run(s, stdout=subprocess.PIPE)
    res_str = res.stdout.decode('utf-8')
    if "Connection failed" in res_str or "ERROR" in res_str:
      print('Yhteys pätki toisen kerran')
      time.sleep(5)
      res = subprocess.run(s, stdout=subprocess.PIPE)
      res_str = res.stdout.decode('utf-8')
  return res_str

#def bad_battery_eq3s():
#  low_battery = []
#  for eq3 in eq3s:
#    if "low battery" in eq3_command(eq3 + " sync"):
#      low_battery.append(mac_to_room(eq3))
#  return low_battery

# input: makkari offset -1
#        työkkäri-makkari timer 12:00-13:00 17
def human_to_machine(str):
  str = remove_extra_spaces(str)
  selected_rooms = str.split(" ")[0].split("-")
  print(str)
  # No command -> return status
  if len(str.split(" ")) == 1:
    command = " status"
  else:
    command = " " + (" ").join(str.split(" ")[1:])
  # TODO: jaa osiin, alla vain vakiokomennot
  
  res = []
  if selected_rooms[0] == "kaikki":
    for eq3 in eq3s:
      res.append(replace_macs_to_names(eq3_command_with_extras(eq3 + command)))
  else:
    for room in selected_rooms:
      if room in rooms and "eq3" in rooms[room]:
        for eq3 in rooms[room]["eq3"]:
          res.append(replace_macs_to_names(eq3_command_with_extras(eq3 + command)))
      else:
        res.append("Huonetta '" + room + "' ei ole. Valitse jokin näistä: " + ", ".join(rooms) + ". Käyn muut huoneet läpi.")
  return res


def eq3_command_with_extras(str):
  if in_allday_timer_format(str):
    return eq3_command(str + ' 24:00')
  else:
    return eq3_command(str)

def mi_command(mac):
  s = ['/home/lowpaw/Downloads/mi_scripts/LYWSD03MMC.py', '--device', mac, '--count', '1']
  res = subprocess.run(s, stdout=subprocess.PIPE)
  res_str = res.stdout.decode('utf-8')
  return res_str

def mi_to_json(mac):
  res = mi_command(mac)
  print(res)
  mi_json = json.loads("{}")
  try:
    mi_json['temp'] = float(remove_extra_spaces(res.split('Temperature:')[1].split('\nHumidity')[0]))
    mi_json['humidity'] = float(remove_extra_spaces(res.split('Humidity:')[1].split('\nBattery')[0]))
    mi_json['battery'] = float(remove_extra_spaces(res.split('Battery level:')[1].split('\n1 measurem')[0]))
  except:
    mi_json['temp'] = float('nan')
    mi_json['humidity'] = float('nan')
    mi_json['battery'] = float('nan')
  return mi_json
  
def read_mi(s):
  print('olet oikeassa paikassa!')
  s = remove_extra_spaces(s)
  selected_rooms = s.split(" ")[0].split("-")
  res = []
  if selected_rooms[0] == "kaikki":
    for mi in mis:
      res.append(mi_command(mi))
  else:
    for room in selected_rooms:
      if room in rooms and "mi" in rooms[room]:
        for mi in rooms[room]["mi"]:
          print('mi huoneessa: ' + room)
          res.append(replace_macs_to_names(mi_command(mi)))
      else:
        res.append("Huonetta '" + room + "' ei ole. Valitse jokin näistä: " + ", ".join(rooms) + ". Käyn muut huoneet läpi.")
  return res
    
  
"""
# command : 'mac timer mon 19:00-20:00 22.5'
# command is identified by 'timer', number of spaces, and '-' between the times
def in_new_timer_format(command):
  arr = command.split(" ")  
  if len(arr) == 5 and arr[1] == 'timer':
    times = arr[3].split("-")
    return len(times) == 2
  return False

# command : 'mac timer mon 22.5'
def in_allday_timer_format(command):
  arr = command.split(" ")
  return (len(arr) == 4 and arr[1] == 'timer')
"""
def remove_extra_spaces(str):
  arr = str.split(" ")
  i = 0
  while i < len(arr):
    if arr[i] == '':
      arr.pop(i)
    else:
      i = i+1
  return " ".join(arr)
  
"""  
def str_to_time(str):
    if str == '24:00':
        return datetime.strptime('1900-01-02 00:00', '%Y-%m-%d %H:%M')
    else:
        return datetime.strptime(str, '%H:%M')

def new_timer_command(old_command, new_command):
    # Convert str to time
    try:
        t1 = str_to_time(new_command.split('-')[0])
        t2 = str_to_time(new_command.split('-')[1].split(" ")[0])
        temp = new_command.split(" ")[1]
        temp_float = float(temp)
    except:
        return "ERROR: Invalid syntax. Example of a valid input: '9:30-10:00 18.5'"
    if t1 >= t2:
        return "ERROR: Invalid time period."

    if t1.strftime("%M")[-1] != '0' or t2.strftime("%M")[-1] != '0':
        return "ERROR: The times must be rounded to ten minutes. For example, 19:11 is invalid and 19:10 is valid."

    if 2*temp_float % 1 != 0.0:
        return "ERROR: Temperature must be rouded to a half of a celsius."

    if temp_float < 5 or temp_float > 29.5:
        return "ERROR: Temperature must lie in between 5 and 29.5."
    
    old = old_command.split(' ')
    
    # Look for the indices where to remove the old array
    # we keep [0:start_ind] and [end_ind:]
    i = 0
    start_ind = -1
    while start_ind == -1 and i < len(old)/2:
        if str_to_time(old[1+2*i]) >= t1:
            start_ind = 2*i+1
        i = i+1
    
    i = 0
    end_ind = -1
    while end_ind == -1 and i < len(old)/2:
        if str_to_time(old[1+2*i]) > t2:
            end_ind = 2*i
        i = i+1
    
    # Create new array, from the start
    if start_ind != -1:
        new_arr = old[0:start_ind]
    else:
        new_arr = []
    
    # Add new timer settings
    new_arr.append(t1.strftime("%H:%M"))
    new_arr.append(temp)
    if new_command.split('-')[1].split(" ")[0] == '24:00':
        new_arr.append('24:00')
    else:
        new_arr.append(t2.strftime("%H:%M"))
    
    # Add the rest of the old timer setting
    if end_ind != -1:
        new_arr = new_arr + old[end_ind:]
    
    # Remove possible '00:00'
    if new_arr[1] == '00:00':
        new_arr = new_arr[2:]
    
    # Cleanup: remove the same consecutive temperatures
    i = 0
    while i+2 < len(new_arr):
        if float(new_arr[i]) == float(new_arr[i+2]):
            new_arr = new_arr[0:i] + new_arr[(i+2):]
        else:
            i = i+2

    # See if the schedule is too long
    if len(new_arr)/2 > 7:
        return "ERROR: Too complicated schedule. Up to seven events are possible per day."
    return " ".join(new_arr)


#Luo funktio : timer1 == timer2;

def set_different_days_with_new_timer_command(old, new_command, days):
  #old = [mon: '', ...]
  #new_command = 
  print(old)
  print(new_command)
  print(days)
  
  if days == 'everyday':
    day_set = ['sat', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri']
  elif days == 'weekend':
    day_set = ['sat', 'sun']
  else:
    day_set = [days] # eli esim. ['mon']
  
  all_equal = True
  timer_first = new_timer_command(old[day_set[0]], new_command)
  print('Eka päivä:')
  print(timer_first)
  
  for day in day_set:
    if not timers_equal(timer_first, new_timer_command(old[day], new_command)):
      all_equal = False
  
  if all_equal:
    print('kaikki päivät samanlaisia; lopullinen komento:')
    print(days + ' ' + timer_first)
    return [days + ' ' + timer_first]
    
  else:
    res_set = []
    print('kaikki päivät ei samanlaisia; lopulliset komennot:')
    for day in day_set:
      print(day + ' ' + new_timer_command(old[day], new_command))
      res_set.append(day + ' ' + new_timer_command(old[day], new_command))
    return res_set

# e.g., '25 10:00 13 24:00'
def timers_equal(one, other):
  a = one.split(' ')
  b = other.split(' ')
  if len(a) != len(b):
    return False
  
  for i in range(len(a)):
    if i%2 == 0:
      if float(a[i]) != float(b[i]):
        return False
    else:
      if str_to_time(a[i]) != str_to_time(b[i]):
        return False
  return True
"""
  
