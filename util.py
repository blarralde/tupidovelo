"""Utility functions.
"""

import math

ROCK = 0
PAPER = 1
SCISSORS = 2

def PrettyChoice(choice):
  if choice == ROCK:
    return "r"
  elif choice == SCISSORS:
    return "s"
  else:
    return "p"


def MeanStdv(x):
  """Calculate mean and standard deviation of set of observations.

  mean = {\sum_i x_i \over n}
  std = sqrt(\sum_i (x_i - mean)^2 \over n-1)

  http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html
  """
  n, mean, std = len(x), 0, 0
  for a in x:
    mean = mean + a
  mean = mean / float(n)
  for a in x:
    std = std + (a - mean)**2
  std = math.sqrt(std / float(n-1))
  return mean, std


def PrintScoreboard(game):
  print """Wins
Us\tThem
%(wins_us)d\t%(wins_them)d
""" % {"wins_us": game.wins_us,
       "wins_them": game.wins_them}
