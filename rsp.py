import random

ROCK = 0
PAPER = 1
SCISSORS = 2
ALL_OPTIONS = [ROCK, PAPER, SCISSORS]

WINS_US = 0
WINS_THEM = 1
TIE = 2

class RandomOpponent(object):
  def Pick(self, game):
    return random.choice(ALL_OPTIONS)


class RandomBeater(object):
  def Pick(self, game):
    frequency_rock = 0
    frequency_paper = 0
    frequency_scissors = 0
    for choice_them in game.choices_them[-100:]:
      if choice_them == ROCK:
        frequency_rock += 1
      elif choice_them == PAPER:
        frequency_paper += 1
      elif choice_them == SCISSORS:
        frequency_scissors += 1

    print "current stats: r/p/s | %d/%d/%d" % (frequency_rock, frequency_paper, frequency_scissors)

    if (frequency_rock < frequency_scissors and frequency_rock < frequency_paper):
      return PAPER
    elif (frequency_paper < frequency_scissors and frequency_paper < frequency_rock):
      return SCISSORS
    else:
      return ROCK


class Game(object):
  def __init__(self):
    self.wins_us = 0
    self.wins_them = 0
    self.current_round = 1
    self.rounds_results = []
    self.choices_us = []
    self.choices_them = []

  def ResolveRound(self, choice_us, choice_them):
    print "%d Choice us: %s | Choice them: %s\n" % (self.current_round, PrettyChoice(choice_us), PrettyChoice(choice_them))
    self.choices_us.append(choice_us)
    self.choices_them.append(choice_them)

    if choice_them == choice_us:
      self.rounds_results.append(TIE)
    elif ((choice_us == ROCK and choice_them == SCISSORS) or
         (choice_us == PAPER and choice_them == ROCK) or
         (choice_us == SCISSORS and choice_them == PAPER)):
      self.wins_us += 1
      self.rounds_results.append(WINS_US)
    else:
      self.wins_them += 1
      self.rounds_results.append(WINS_THEM)

    self.current_round += 1

  def PrintScoreboard(self):
    print """Wins
Us\tThem
%(wins_us)d\t%(wins_them)d
""" % {"wins_us": self.wins_us,
       "wins_them": self.wins_them}

def PrettyChoice(choice):
  if choice == ROCK:
    return "r"
  elif choice == SCISSORS:
    return "s"
  else:
    return "p"

if __name__ == "__main__":
  random_opponent = RandomOpponent()
  random_beater = RandomBeater()
  game = Game()

  for i in range(10000):
    choice_them = random_opponent.Pick(game)
    choice_us = random_beater.Pick(game)
    game.ResolveRound(choice_us, choice_them)

  game.PrintScoreboard()

