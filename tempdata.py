import util
from datetime import datetime

class Tempdata:
  def __init__(self, filename, timestep):
    self.hourly_external_temps = [(l.strip().split(',')[0], util.f_to_c(float(l.strip().split(',')[1].strip()))) for l in open("hourly-temp.csv").readlines()]
    self.timestep = timestep
    self.timespan = int(len(self.hourly_external_temps) / self.timestep)
    
  def external_temp(self, t):
    """Get the real external temperature at any given time"""
    return self.hourly_external_temps[int(t * self.timestep)][1]

  def steptime_to_date(self, t):
    """Map time steps to real datetimes"""
    hourly_time = datetime.strptime(self.hourly_external_temps[int(t * self.timestep)][0], "%Y-%m-%d %H:%M:%S")
    return hourly_time.replace(minute = int((t % int(1 / self.timestep)) * 60 * self.timestep))


