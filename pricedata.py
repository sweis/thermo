import util
from datetime import datetime

class Pricedata:
  def __init__(self, filename):
    file = open(filename)
    prices = [l.strip().split(',') for l in file.readlines()]
    file.close()
    self.price_map = { }
    for p in prices:
      d = datetime.strptime(p[0], "%Y-%m-%d %H:%M:%S")
      self.price_map[d] = float(p[1].strip())

  def price(self, time):
    round_down = time.replace(minute = 0)
    return float(self.price_map[round_down])