from discord.ext import commands


# Insufficient funds
class InsufficientFunds(commands.CommandError):
    pass


# Bet is too small
class MinimumBet(commands.CommandError):
    def __init__(self, minimum_bet):
        self.minimum_bet = minimum_bet
