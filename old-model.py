from math import exp
from math import sqrt
from random import normalvariate
from datetime import datetime

### Physical Parameters 
h = 1 / 60.0  # Time step in hours
h_seconds = h * 3600
sqrt_h_seconds = sqrt(h_seconds)
C = 10.0  # Thermal capacitance in kWh / degree Celcius
R = 2.0  # Thermal resistance in degrees Celcius / kW
P = 14.0  # Average energy transfer rate in kW
theta_s = 22  # Temperature setting
eta = 2.5  # Load efficiency  
delta = 0.5  # Thermostat deadband in degrees Celcius
a = exp(-h/C*R)
sigma = 0.01  # Noise standard deviation, degrees Celcius / sqrt(s)

### Utility functions

def c_to_f(c):
  return c*9.0/5 + 32

def f_to_c(f):
  return (f-32.0)*5.0/9

# Normal distributiom of noise
def w():
  return 0
  # Disabling noise for now
  #return normalvariate(0, sqrt_h_seconds * sigma)

def power(minutes):
  """Returns kwh consumed in the given number of minutes"""
  return (1.0/eta * P * minutes) / 60.0

### Real price data

prices = [l.strip().split(',') for l in open("hourly-price.csv").readlines()]
price_map = { }
for p in prices:
  price_map[p[0]] = float(p[1].strip())

def market_price(t):
  round_down = steptime(t).replace(minute = 0)
  return float(price_map[str(round_down)])

### Real temperature data

# Read in temperature readings
hourly_external_temps = [(l.strip().split(',')[0], f_to_c(float(l.strip().split(',')[1].strip()))) for l in open("hourly-temp.csv").readlines()]

def external_temp(t):
  """Get the real external temperature at any given time"""
  return hourly_external_temps[int(t*h)][1]

def steptime(t):
  """Map time steps to real datetimes"""
  hourly_time = datetime.strptime(hourly_external_temps[int(t*h)][0], "%Y-%m-%d %H:%M:%S")
  return hourly_time.replace(minute = int((t % int(1/h)) * 60 * h))

# How long the data runs for in units of timesteps
timespan = int(len(hourly_external_temps)/h)

### Internal temperature model

# Memoize the internal temps
Theta = { }
def theta(t, thermostat):
  if t <= 0:
    return theta_s  # Start out at the setpoint
  if not Theta.has_key(thermostat):
    Theta[thermostat] = [-1] * int(timespan / h)
  if Theta[thermostat][t] == -1:
    Theta[thermostat][t] = a * theta(t-1, thermostat) + \
      (1.0-a) * (external_temp(t-1) - thermostat(t-1) * R * P) + w()
    if Theta[thermostat][t] < theta_s - 10:
      Theta[thermostat][t] = theta_s - 10   # Magic house that does not cool below 12 C
  return Theta[thermostat][t]

### Dumb thermostat model
M = [-1] * int(timespan / h)
def dumb(t):
  """Dumb Thermostat with +/- delta dead zone"""
  if t <= 0:
    return 0
  if M[t] == -1:
    theta_t = theta(t-1, dumb)
    if theta_t > theta_s + delta:
      M[t] = 1
    elif theta_t < theta_s - delta:
      M[t] = 0
    else:
      M[t] = dumb(t-1)
  return M[t]

PRICE_AWARE = [-1] * int(timespan / h)
def price_aware(t):
  if t <= 0:
    return 0
  if PRICE_AWARE[t] == -1:
    theta_t = theta(t-1, price_aware)
    threshold = delta
    time = steptime(t).replace(minute = 0)
    if price_map.has_key(str(time)):
      price = price_map[str(time)]
      if price > 40:
        threshold = 1
    if theta_t > theta_s + threshold:
      PRICE_AWARE[t] = 1
    elif theta_t < theta_s - delta:
      PRICE_AWARE[t] = 0
    else:
      PRICE_AWARE[t] = price_aware(t-1)
  return PRICE_AWARE[t]

PRICE_AWARE_2 = [-1] * int(timespan / h)
def price_aware_2(t):
    if t <= 0:
      return 0
    if PRICE_AWARE_2[t] == -1:
      theta_t = theta(t-1, price_aware_2)
      threshold = delta
      time = steptime(t).replace(minute = 0)
      if price_map.has_key(str(time)):
        price = price_map[str(time)]
        if price > 40 and theta_t > theta_s:
          threshold = 1
          ext = external_temp(t)
          if price > 100 and ext < 80:
            threshold = 2
      if theta_t > theta_s + threshold:
        PRICE_AWARE_2[t] = 1
      elif theta_t < theta_s - delta:
        PRICE_AWARE_2[t] = 0
      else:
        PRICE_AWARE_2[t] = price_aware_2(t-1)
    return PRICE_AWARE_2[t]

# Compute the modeled run cycles
def ComputeCost(thermostat):
  last = None
  lmp_cost = 0
  total_kwh = 0
  max_temp = 0
  for i in range(0, timespan):
    if theta(i, thermostat) > max_temp:
      max_temp = theta(i, thermostat)
    if last == None and thermostat(i):
      last = i
    elif last != None and not thermostat(i):
      start = steptime(last)
      last = None
      end = steptime(i)
      minutes = (end - start).seconds / 60.0
      kwh = power(minutes)
      start_round_down = start.replace(minute=0)
      end_round_down = end.replace(minute=0)
      end_round_up = end.replace(minute=0, hour=((end.hour + 1) % 24))   
      if not price_map.has_key(str(start_round_down)):
        continue
      if not price_map.has_key(str(end_round_down)):
        continue
      if not price_map.has_key(str(end_round_up)):
        continue
      price = 0
      if start_round_down == end_round_down:
        start_price = float(price_map[str(start_round_down)])
        end_price = float(price_map[str(end_round_up)])
        price = ((end_price - start_price) / 60.0) * minutes + start_price 
      else:
        # We're stradding an hour, so use that price. Fudging a bit
        price = float(price_map[str(end_round_down)])
      if price > 40:
        cost = price * kwh / 1000.0
        # Tally usage
        lmp_cost += cost
        total_kwh += kwh  
  return "$%g for %g kWh eligible, max_temp %g" % (lmp_cost, total_kwh, c_to_f(max_temp))

# Populate the data. Could call theta(timespan) and memoize, but that exceeds the recursion depth.
#print "Control: ", ComputeCost(dumb)
#print "Price aware: ", ComputeCost(price_aware)
print "Price aware 2: ", ComputeCost(price_aware_2)

#start_output = False
#for t in range(0, timespan):
#  try:
#    time = steptime(t)
#    ext_temp = c_to_f(external_temp(t))
#    price = market_price(t)
#    start_output = start_output or dumb(t) or price_aware(t) or price_aware_2(t)
#    if start_output:
#      print "%s, %s, %s, %s, %s, %s, %s, %s, %s" % (time, ext_temp, price, c_to_f(theta(t, dumb)), dumb(t), c_to_f(theta(t, price_aware)), price_aware(t), c_to_f(theta(t, price_aware_2)), price_aware_2(t))
#  except KeyError:
#    # Ignore 
#    continue