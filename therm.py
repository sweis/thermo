class Thermostat:
  def __init__(self, setting_celcius = 22, deadband_delta_celcius = 0.5):
    self.setting = 22
    self.delta = 0.5
    self.state = 0
    
  def eval(self, temperature):
    if temperature > self.setting + self.delta:
      self.state = 1
    elif temperature < self.setting - self.delta:
      self.state = 0
    return self.state