from datetime import timedelta
from pricedata import Pricedata

class GreedyStrategy:
  def __init__(self, price_filename, price_threshold = 40, temp_swing_celcius = 1.0):
    pricedata = Pricedata(price_filename)
    price_dates = []
    price_map = pricedata.price_map
    for (date, price) in price_map.iteritems():
      if price > price_threshold:
        price_dates.append((price, date))
    price_dates = sorted(price_dates, reverse=True)
    self.states = { }
    self.temp_swing = temp_swing_celcius
    for (price, date) in price_dates:
      if price_map.has_key(date):
        # Precharge the preceeeding hour
        delta = timedelta(0, 3600, 0)
        prev_hour = date - delta
        # See if we can pre-charge the preceeding hour
        if price_map.has_key(prev_hour):
          # If so, schedule both an hour of pre-charging and an hour of curtailment
          self.states[prev_hour] = "Precharge"
          price_map.pop(prev_hour)
          self.states[date] = "Curtail"
          price_map.pop(date)
    self.current_swing = 0

  def iterate(self, datetime):
    d = datetime.replace(minute = 0)
    if self.states.has_key(d):
      state = self.states[d]
      if state == "Curtail":
        self.current_swing = self.temp_swing
      elif state == "Precharge":
        self.current_swing = -self.temp_swing
    else:
      self.current_swing = 0
    
