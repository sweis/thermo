import therm

from model import Model
from pricedata import Pricedata
from strategy import GreedyStrategy
from tempdata import Tempdata

import util

timestep = 1/60.0
tempdata = Tempdata("hourly-temp.csv", timestep)

pricedata = Pricedata("hourly-price.csv")

no_cooling_model = Model(thermostat = therm.NoThermostat(), time_step_in_hours = timestep)
control_model = Model(thermostat = therm.ControlThermostat(), time_step_in_hours = timestep)

greedy_strategy = GreedyStrategy("hourly-price.csv")
experiment_model = Model(thermostat = therm.CurtailedThermostat(strategy = greedy_strategy), time_step_in_hours = timestep)
experiment_model_2 = Model(thermostat = therm.HarshCurtailedThermostat(strategy = greedy_strategy), time_step_in_hours = timestep)

total_cost_control = 0
total_cost_experiment = 0
total_cost_experiment_2 = 0
for i in range(1, tempdata.timespan):
  ext_temp = tempdata.external_temp(i)
  no_cooling_model.iterate(ext_temp)
  control_model.iterate(ext_temp)
  d = tempdata.steptime_to_date(i)
  greedy_strategy.iterate(d)
  experiment_model.iterate(ext_temp)
  experiment_model_2.iterate(ext_temp)
  price_mwh = pricedata.price(d)
  control_cost = control_model.power_cost(price_mwh)
  experiment_cost = experiment_model.power_cost(price_mwh)
  experiment_cost_2 = experiment_model_2.power_cost(price_mwh)
  total_cost_control += control_cost
  total_cost_experiment += experiment_cost
  total_cost_experiment_2 += experiment_cost_2
  if i % 15 == 0:
    # util.c_to_f(ext_temp), util.c_to_f(control_model.temp), util.c_to_f(experiment_model.temp), 
    print "%s, %.0f, %.0f, %.0f, %.0f, $%.2f, $%.2f, $%.2f" % (d, \
      util.c_to_f(ext_temp), util.c_to_f(control_model.temp), util.c_to_f(experiment_model.temp), util.c_to_f(experiment_model_2.temp), \
      total_cost_control, total_cost_experiment, total_cost_experiment_2)
