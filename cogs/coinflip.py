import random

from discord.ext import commands

from config import database
from helpers import user_services
from custom_errors import InsufficientFunds, MinimumBet


class CoinFlip(commands.Cog):
    """
    Use command `coinflip <bet>` to try your luck in a coinflip game!
    """

    def __init__(self):
        pass

    # Coin flip !coinflip <bet>, you have 50% to win or lose
    @commands.command(name='coinflip', aliases=['cf'])
    async def coinflip(self, ctx, bet):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        player_bal = user_services.get_user_balance(user_id, guild_id)
        minimum_bet = database.guilds.find_one({'guild_id': guild_id}).get('minimum_bet_coinflip')

        if bet == 'all':
            bet = player_bal
        else:
            try:
                bet = int(bet)
            except ValueError:
                raise commands.UserInputError

        if bet < minimum_bet:
            raise MinimumBet(minimum_bet)
        elif player_bal < bet:
            raise InsufficientFunds
        else:
            if random.randint(0, 1):
                database.users.update_one({'user_id': user_id, 'guild_id': guild_id}, {'$inc': {'balance': bet}})
                await ctx.send(f'{ctx.author.mention} won {bet} coins!')
            else:
                database.users.update_one({'user_id': user_id, 'guild_id': guild_id}, {'$inc': {'balance': -bet}})
                await ctx.send(f'{ctx.author.mention} lost {bet} coins!')

    # Error handling for coinflip
    @coinflip.error
    async def coinflip_error(self, ctx, error):
        if isinstance(error, MinimumBet):
            await ctx.send(f'`The minimum bet is {error.minimum_bet} coins!`')
        elif isinstance(error, InsufficientFunds):
            await ctx.send('`You have insufficient funds!`')
        elif isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'bet':
                await ctx.send("`You must enter a bet!`")
        elif isinstance(error, commands.UserInputError):
            await ctx.send("`Bet must be an integer or all!`")


def setup(bot):
    bot.add_cog(CoinFlip())