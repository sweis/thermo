from math import exp
from math import sqrt
from random import normalvariate

class Model:
  """Thermal model"""
  def __init__(self,
      thermostat = None,
      thermal_capacitance_kwh_per_celcius = 10.0,
      ave_energy_transfer_rate_kW = 14.0,
      thermal_resistance_celcius_per_kw = 2.0,
      time_step_in_hours = 1/60.0,
      std_dev_celcius_per_sqrt_s = 0.01,
      load_efficiency = 2.5,
      internal_temp_celcius = 22):
    self.therm = thermostat
    self.C = thermal_capacitance_kwh_per_celcius
    self.P = ave_energy_transfer_rate_kW
    self.R = thermal_resistance_celcius_per_kw
    self.h = time_step_in_hours
    self.a = exp(-self.h / self.C * self.R)
    self.sigma = std_dev_celcius_per_sqrt_s * sqrt(self.h * 3600)
    self.eta = load_efficiency
    self.temp = internal_temp_celcius
    self.kwh_per_timestep = (1.0 / self.eta * self.P) * self.h
    self.kwh = 0
    
  def w(self):
    """Returns a normal distribution of noise"""
    return 0
    #return normalvariate(0, self.sigma)
    
  def power_usage(self):
    return self.therm.state * self.kwh_per_timestep

  def power_cost(self, cost_mwh):
    return self.power_usage() * cost_mwh / 1000.0

  def iterate(self, external_temp_celcius):
    self.temp = self.a * self.temp + \
      (1.0 - self.a) * (external_temp_celcius - self.therm.eval(self.temp) * self.R * self.P) + \
      self.w()
    if self.temp < 12:
      self.temp = 12   # Magic so that it does not cool below 12 C
    self.kwh += self.power_usage()