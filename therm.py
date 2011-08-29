from strategy import GreedyStrategy

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
    
class CurtailedThermostat:
  def __init__(self, strategy, setting_celcius = 22, deadband_delta_celcius = 0.5):
    self.setting = setting_celcius
    self.delta = deadband_delta_celcius
    self.state = 0
    self.strategy = strategy

  def eval(self, temperature):
    if temperature > self.setting + self.delta + self.strategy.current_swing:
      self.state = 1
    elif temperature < self.setting - self.delta + self.strategy.current_swing:
      self.state = 0
    return self.state

class HarshCurtailedThermostat:
  def __init__(self, strategy, setting_celcius = 22, deadband_delta_celcius = 0.5):
    self.setting = setting_celcius
    self.delta = deadband_delta_celcius
    self.state = 0
    self.strategy = strategy

  def eval(self, temperature):
    if self.strategy.current_swing > 0:
      # If curtailment is on, shut off regardless of the temperature
      self.state = 0
    elif temperature > self.setting + self.delta:
      self.state = 1
    elif temperature < self.setting - self.delta:
      self.state = 0
    return self.state

