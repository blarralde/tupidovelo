"""
Rock, Paper, Scissors battleground simulator.

Usage:
1. Pit every strategy against each other:

  python simulator.py --mode=ffa


2. Pit a single strategy against all the others including itself:

  python simulator.py --mode=1vsall --strategy=Random

"""
__author__ = "Benjamin Larralde, Juan Alonso"

import logging
import math
import random
import sys

import util
import optparse

ROCK = 0
PAPER = 1
SCISSORS = 2
ALL_OPTIONS = [ROCK, PAPER, SCISSORS]

KEY_WINS_AGAINST_VALUE = {ROCK: SCISSORS,
                          PAPER: ROCK,
                          SCISSORS: PAPER}

KEY_LOSES_AGAINST_VALUE = {ROCK: PAPER,
                           PAPER: SCISSORS,
                           SCISSORS: ROCK}

WINS1 = 0
WINS2 = 1
TIE = 2


class Game(object):
  def __init__(self, opponent1, opponent2):
    self.wins1 = 0
    self.wins2 = 0
    self.losses1 = 0
    self.losses2 = 0
    self.current_round = 1
    self.rounds_results = []
    self.choices1 = []
    self.choices2 = []
    self.opponent1 = opponent1
    self.opponent1.SetPlayerId(1)
    self.opponent2 = opponent2
    self.opponent2.SetPlayerId(2)

  def ResolveRound(self, choice1, choice2):
    logging.debug("%d Choice us: %s | Choice them: %s" %
       (self.current_round,
        util.PrettyChoice(choice1),
        util.PrettyChoice(choice2)))

    self.choices1.append(choice1)
    self.choices2.append(choice2)

    if choice2 == choice1:
      self.rounds_results.append(TIE)
    elif ((choice1 == ROCK and choice2 == SCISSORS) or
          (choice1 == PAPER and choice2 == ROCK) or
          (choice1 == SCISSORS and choice2 == PAPER)):
      self.wins1 += 1
      self.losses2 += 1
      self.rounds_results.append(WINS1)
    else:
      self.wins2 += 1
      self.losses1 += 1
      self.rounds_results.append(WINS2)

    self.current_round += 1


class Oracle(object):
  def __init__(self, caller_strategy):
    self.caller_strategy = caller_strategy
    self._is_always_the_same = True
    self._is_human_random = True

  def GetNextMove(self, game):
    next_choice = random.choice(ALL_OPTIONS)

    if self.caller_strategy.GetPlayerId() == 1:
      choices_us = game.choices1
    else:
      choices_us = game.choices2

    if self.caller_strategy.GetPlayerId() == 1:
      choices_them = game.choices2
    else:
      choices_them = game.choices1

    if self.IsAlwaysTheSame(game, choices_us, choices_them):
      if game.current_round == 1:
        next_choice = random.choice(ALL_OPTIONS)
      else:
        next_choice = KEY_LOSES_AGAINST_VALUE[choices_them[-1]]
    elif self.IsHumanRandom(game, choices_us, choices_them):
      if game.current_round == 1:
        next_choice = random.choice(ALL_OPTIONS)
      else:
        choices = set(ALL_OPTIONS) -  set([choices_them[-1]])
        next_choice = random.choice(list(choices))

    return next_choice


  def IsAlwaysTheSame(self, game, choices_us, choices_them):
    if not self._is_always_the_same:
      return False
    else:
      if game.current_round <= 2:
        return False
      else:
        if choices_them[-2] != choices_them[-1]:
          self._is_always_the_same = False

        return self._is_always_the_same

  def IsHumanRandom(self, game, choices_us, choices_them):
    if not self._is_human_random:
      return False
    else:
      if game.current_round <= 2:
        return False
      else:
        if choices_them[-2] == choices_them[-1]:
          self._is_human_random = False

        return self._is_human_random


class Strategy(object):
  def Pick(self):
    raise Exception("AbstractStrategy")

  def SetPlayerId(self, player_id):
    self.player_id = player_id

  def GetPlayerId(self):
    return self.player_id


class SimpleLearner(Strategy):
  def __init__(self):
    self._oracle = Oracle(self)

  def Pick(self, game):
    return self._oracle.GetNextMove(game)


class AlwaysTheSame(Strategy):
  """Uses the same choice determined at init time on every round."""
  def __init__(self):
    self.choice = random.choice([ROCK, SCISSORS, PAPER])

  def Pick(self, game):
    return self.choice


class HumanRandom(Strategy):
  """Picks random elements without repeating."""
  def Pick(self, game):
    if game.current_round == 1:
        return ROCK

    if self.GetPlayerId() == 1:
      choices_us = game.choices1
    else:
      choices_us = game.choices2

    if choices_us[-1] == ROCK:
      return random.choice([SCISSORS, PAPER])
    elif choices_us[-1] == SCISSORS:
      return random.choice([ROCK, PAPER])
    else:
      return random.choice([ROCK, SCISSORS])


class OppositeOfLast(Strategy):
  """Picks what would be won over by the last option the oppponent picked."""
  def Pick(self, game):
    if game.current_round == 1:
        return ROCK

    if self.GetPlayerId() == 1:
      choices_them = game.choices2
    else:
      choices_them = game.choices1

    if choices_them[-1] == ROCK:
        return SCISSORS
    elif choices_them[-1] == SCISSORS:
        return PAPER
    else:
        return ROCK


class BeaterOfLast(Strategy):
  """Picks what would win the last option the opponent picked."""
  def Pick(self, game):
    if game.current_round == 1:
        return ROCK

    if self.GetPlayerId() == 1:
      choices_them = game.choices2
    else:
      choices_them = game.choices1

    if choices_them[-1] == ROCK:
        return PAPER
    elif choices_them[-1] == SCISSORS:
        return ROCK
    else:
        return SCISSORS


class Random(Strategy):
  def Pick(self, game):
    return random.choice(ALL_OPTIONS)


class RandomBeater(Strategy):
  """Tries to beat a random strategy by guessing next option."""
  def __init__(self):
    self.freq_rock = 0
    self.freq_paper = 0
    self.freq_scissors = 0

  def Pick(self, game):
    if game.current_round > 1:
      if self.GetPlayerId() == 1:
        choices_them = game.choices2
      else:
        choices_them = game.choices1

      last_choice = choices_them[-1]

      if last_choice == ROCK:
        self.freq_rock += 1 * self.GetRoundWeight(game.current_round)
      elif last_choice == PAPER:
        self.freq_paper += 1 * self.GetRoundWeight(game.current_round)
      elif last_choice == SCISSORS:
        self.freq_scissors += 1 * self.GetRoundWeight(game.current_round)

    logging.debug("current stats: r/p/s | %d/%d/%d" % (self.freq_rock,
                                                       self.freq_paper,
                                                       self.freq_scissors))

    if (self.freq_rock < self.freq_scissors and
        self.freq_rock < self.freq_paper):
      return PAPER
    elif (self.freq_paper < self.freq_scissors and
          self.freq_paper < self.freq_rock):
      return SCISSORS
    elif (self.freq_scissors < self.freq_rock and
          self.freq_scissors < self.freq_paper):
      return ROCK
    # Ties
    elif (self.freq_rock == self.freq_scissors):
      return random.choice([PAPER, ROCK])
    elif (self.freq_rock == self.freq_paper):
      return random.choice([PAPER, SCISSORS])
    elif (self.freq_paper == self.freq_scissors):
      return random.choice([SCISSORS, ROCK])
    # Complete tie
    else:
      return random.choice([ROCK, SCISSORS, PAPER])

  def GetRoundWeight(self, round):
    """Returns: the weight given to the option picked in a given round."""
    return 1


class RandomBeaterWeighted(RandomBeater):
  def GetRoundWeight(self, round):
    """Returns: the weight given to the option picked in a given round."""
    return round


class SequentialPicker(Strategy):
  """Picks PAPER, ROCK, SCISSORS in series."""
  def __init__(self):
    self.last_choice = ROCK

  def Pick(self, game):
    if self.last_choice == ROCK:
      next_choice = PAPER
    elif self.last_choice == PAPER:
      next_choice = ROCK
    else:
      next_choice = SCISSORS
    self.last_choice = next_choice
    return next_choice


class DifferentEveryN(Strategy):
  """Picks one option, repeats it every X rounds and then picks a different
  option.

  PAPER, ROCK, SCISSORS, SCISSORS, PAPER, PAPER, ROCK, ROCK, SCISSORS, SCISSORS, ...
  """
  def __init__(self):
    self.last_choice = random.choice(ALL_OPTIONS)
    self.repeats = random.randint(1, 10)

  def Pick(self, game):
    if game.current_round % self.repeats != 0:
      return self.last_choice
    else:
      choices = set(ALL_OPTIONS) -  set([self.last_choice])
      self.last_choice = random.choice(list(choices))
      return self.last_choice


class DifferentEveryNAndEveryCycle(DifferentEveryN):
  """Picks one option, repeats it N rounds, then picks a new option and a new N.
  """
  def __init__(self):
    self.last_choice = random.choice(ALL_OPTIONS)
    self.repeats = random.randint(1, 10)
    self.cycle_counter = 1

  def Pick(self, game):
    if self.cycle_counter % self.repeats != 0:
      self.cycle_counter += 1
      return self.last_choice
    else:
      self.cycle_counter = 1
      self.repeats = random.randint(1, 10)
      choices = set(ALL_OPTIONS) -  set([self.last_choice])
      self.last_choice = random.choice(list(choices))
      return self.last_choice


class BrainDamagedLose(Strategy):
  def __init__(self):
    self.last_choice = random.choice(ALL_OPTIONS)

  def Pick(self, game):
    if game.current_round % 2 == 0:
      return self.last_choice
    else:
      return KEY_LOSES_AGAINST_VALUE[self.last_choice]


class BrainDamagedWin(Strategy):
  def __init__(self):
    self.last_choice = random.choice(ALL_OPTIONS)

  def Pick(self, game):
    if game.current_round % 2 == 0:
      return self.last_choice
    else:
      return KEY_WINS_AGAINST_VALUE[self.last_choice]


class DifferentEvery2(DifferentEveryN):
  def __init__(self):
    self.last_choice = random.choice(ALL_OPTIONS)
    self.repeats = 2

class SequentialExponentialPicker(Strategy):
  """Picks PAPER, ROCK, SCISSORS in series of exponential repetions.

  PAPER, ROCK, SCISSORS, PAPER, PAPER, ROCK, ROCK, SCISSORS, SCISSORS, ...
  """
  def __init__(self):
    self.last_choice = ROCK

  def Pick(self, game):
    log3 = math.log(game.current_round, 3)
    return (int(log3) + 1) % 3


def RunExperiment(strategy1, strategy2, games, rounds_per_game):
  """Runs a series of games and calculates stats from the pov of opponent1.

  Returns:
    Mean, stddev over the number of times that strategy of opponent 1 wins
    over the strategy of opponent 2 when playing "games" number of games with
    rounds_per_game.
  """
  wins = []
  for game_idx2 in range(games):
    inner_wins = 0
    for game_idx in range(games):
      opponent1 = strategy1()
      opponent2 = strategy2()
      game = Game(opponent1, opponent2)

      for i in range(rounds_per_game):
        choice1 = opponent1.Pick(game)
        choice2 = opponent2.Pick(game)
        game.ResolveRound(choice1, choice2)

      inner_wins += game.wins1 - game.losses1

    wins.append(float(inner_wins)/games)
    logging.debug("game_idx %d | %.2f" % (game_idx2, wins[-1]))
  return util.MeanStdv(wins)


def GetStrategies():
  return [AlwaysTheSame,
          HumanRandom,
          OppositeOfLast,
          Random,
          RandomBeater,
          RandomBeaterWeighted,
          BrainDamagedWin,
          BrainDamagedLose,
          SequentialPicker,
          SequentialExponentialPicker,
          SimpleLearner,
          DifferentEvery2,
          DifferentEveryN,
          DifferentEveryNAndEveryCycle,
          BeaterOfLast]


def GetPairings(options):
  strategies = GetStrategies()
  pairings = []
  if options.mode == "ffa":
    for i in range(len(strategies)):
      for j in range(len(strategies)):
        if i <= j:
          pairings.append([strategies[i], strategies[j]])
  elif options.mode == "1vsall":
    assert options.strategy1
    strategy1 = globals()[options.strategy1]
    for strategy in strategies:
      pairings.append([strategy1, strategy])
  else:
    raise Exception("Invalid mode %s" % options.mode)

  return pairings


if __name__ == "__main__":
  parser = optparse.OptionParser()
  parser.add_option("--mode", dest="mode", default="ffa",
                    help="ffa: all strategies against each other. 1vsall:"
                    " strategy opt against every other strategy.")
  parser.add_option("--rounds", dest="rounds", type="int", default=10000)
  parser.add_option("--games", dest="games", type="int", default=10)
  parser.add_option("--strategy1", dest="strategy1")
  (options, args) = parser.parse_args()

  logging.basicConfig(handler=logging.StreamHandler(), level=logging.INFO,
                      format="%(message)s")
  logging.info("Games: %d\nRounds per game: %d\n" % (options.games,
                                                   options.rounds))

  print "%s    %s avScore1  sdScore1" % ("Opponent 1".ljust(30),
                                         "Opponent 2".ljust(30))
  print "-" * 83
  for opponent1, opponent2 in GetPairings(options):
    print "%s    %s" % (opponent1.__name__.ljust(30),
                        opponent2.__name__.ljust(30)),
    mean, stddev = RunExperiment(opponent1, opponent2, options.games,
                                 options.rounds)
    print " %s    %s" % (("%.2f" % mean).rjust(7), ("%.2f" % stddev).rjust(6))

