class NoThermostat:
  def __init__(self):
    self.state = 0

  def eval(self, temperature):
    return self.state

class ControlThermostat:
  def __init__(self, setting_celcius = 22, deadband_delta_celcius = 0.5):
    self.setting = setting_celcius
    self.delta = deadband_delta_celcius
    self.state = 0
    
  def eval(self, temperature):
    if temperature > self.setting + self.delta:
      self.state = 1
    elif temperature < self.setting - self.delta:
      self.state = 0
    return self.state