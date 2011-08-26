from model import Model
from therm import Thermostat


t = Thermostat()
m = Model(thermostat = t)

current_temp = 32
for i in range(1, 1000):
  current_temp = m.internal_temp_celcius(current_temp_celcius = current_temp, external_temp_celcius = 32)
  print current_temp, t.state