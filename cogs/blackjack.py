from discord.ext import commands

from config import minimum_bet
from helpers import user_services
from helpers.blackjack_game import BlackJackGame
from helpers.create_cards_pack import cards_pack


class BlackJack(commands.Cog):
    """
    To start a blackjack game in your channel use the 'blackjack <bet>' command,
    and instead of <bet> put the amount you want to gamble (the value must be a integer).
    After you start a blackjack game use 'hit' command to draw a new card, 'stand' command
    to hold your total and end your turn, 'double' command which is like a 'hit' command,
    but the bet is doubled and you only get one more card, or 'surrender' command to give
    up and lose your bet.
    """

    def __init__(self, bot):
        self.bot = bot
        self.cards_pack = cards_pack
        self.blackjack_games = {}

    @commands.command(name='blackjack', aliases=['bj'])
    async def start_blackjack_game(self, ctx, bet: int):
        player_id = ctx.author.id
        player_bal = user_services.get_user_balance(player_id)

        # Check if player's blackjack game is active
        if player_id in self.blackjack_games:
            await ctx.send('`You are already in a game!`')
        elif bet < minimum_bet:
            await ctx.send(f'`The minimum bet is {minimum_bet} coins!`')
        elif player_bal < bet:
            await ctx.send('`You have insufficient funds!`')
        else:
            current_game = BlackJackGame(bet, ctx.author.name, player_id, [], [], self.cards_pack)
            self.blackjack_games[player_id] = current_game
            if current_game.status == 'finished':
                del self.blackjack_games[player_id]
            await ctx.send(embed=current_game.embed())

    @commands.command(name='hit')
    # Check if player's blackjack game is active
    async def hit_in_blackjack_game(self, ctx):
        if ctx.author.id in self.blackjack_games:
            current_game = self.blackjack_games.get(ctx.author.id)
            current_game.hit_a_card()
            if current_game.status == 'finished':
                del self.blackjack_games[ctx.author.id]
            await ctx.send(embed=current_game.embed())
        else:
            await ctx.send('`You must be in a blackjack game!`')

    @commands.command(name='stand')
    # Check if player's blackjack game is active
    async def stand_in_blackjack_game(self, ctx):
        if ctx.author.id in self.blackjack_games:
            current_game = self.blackjack_games.get(ctx.author.id)
            current_game.stand()
            if current_game.status == 'finished':
                del self.blackjack_games[ctx.author.id]
            await ctx.send(embed=current_game.embed())
        else:
            await ctx.send('`You must be in a blackjack game!`')

    @commands.command(name='double')
    async def double_in_blackjack_game(self, ctx):
        player_id = ctx.author.id
        player_bal = user_services.get_user_balance(player_id)

        # Check if player's blackjack game is active
        if ctx.author.id in self.blackjack_games:
            current_game = self.blackjack_games.get(ctx.author.id)
            # Check if player have more than 2 cards
            if len(current_game.player_cards) > 2:
                await ctx.send('`You can double only in the first round!`')
            # Check if player have sufficient funds for double
            elif player_bal < current_game.bet:
                await ctx.send('`You have insufficient funds!`')
            else:
                current_game.double()
                if current_game.status == 'finished':
                    del self.blackjack_games[ctx.author.id]
                await ctx.send(embed=current_game.embed())
        else:
            await ctx.send('`You must be in a blackjack game!`')

    @commands.command(name='surrender')
    async def surrender_in_blackjack_game(self, ctx):
        # Check if player's blackjack game is active
        if ctx.author.id in self.blackjack_games:
            current_game = self.blackjack_games.get(ctx.author.id)
            current_game.lose_event()
            if current_game.status == 'finished':
                del self.blackjack_games[ctx.author.id]
            await ctx.send(embed=current_game.embed())
        else:
            await ctx.send('`You must be in a blackjack game!`')

    # Error handling
    @start_blackjack_game.error
    async def start_blackjack_game_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'bet':
                await ctx.send("`You must enter a bet!`")
        elif isinstance(error, commands.UserInputError):
            await ctx.send("`Bet must be a integer!`")


def setup(bot):
    bot.add_cog(BlackJack(bot))
