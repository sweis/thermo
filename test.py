from model import Model
from therm import ControlThermostat
from therm import NoThermostat
from tempdata import Tempdata

import util

timestep = 1/60.0
tempdata = Tempdata("hourly-temp.csv", timestep)

no_cooling_model = Model(thermostat = NoThermostat(), time_step_in_hours = timestep)
control_model = Model(thermostat = ControlThermostat(deadband_delta_celcius = 0.5), time_step_in_hours = timestep)
control_model_2 = Model(thermostat = ControlThermostat(deadband_delta_celcius = 1.0), time_step_in_hours = timestep)

turned_on = 0
for i in range(1, tempdata.timespan):
  ext_temp = tempdata.external_temp(i)
  no_cooling_model.iterate(ext_temp)
  control_model.iterate(ext_temp)
  control_model_2.iterate(ext_temp)
  print "%s, %.1f, %.1f, %.1f, %.1f" % (tempdata.steptime_to_date(i), util.c_to_f(ext_temp), \
      util.c_to_f(no_cooling_model.temp), util.c_to_f(control_model.temp), util.c_to_f(control_model_2.temp))
