from discord.ext import commands

from config import database
from helpers import user_services
import discord
import datetime


class User(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # if a user joins a server blackjack-bot creates a entry in database
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        member_id = member.id
        user_services.create_user(member_id, guild_id)

    # if a user left a server blackjack-bot delete his entry in database
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = member.guild.id
        member_id = member.id
        database.users.delete_one({'user_id': member_id, 'guild_id': guild_id})

    # .balance - show a user balance
    @commands.group(name='balance', aliases=['b', 'bal'], help='Shows your balance')
    async def balance(self, ctx):
        if ctx.invoked_subcommand is None:
            user_id = ctx.author.id
            guild_id = ctx.guild.id

            # Get user's balance
            bal = user_services.get_user_balance(user_id, guild_id)

            if bal == 1:
                await ctx.send(f"{ctx.author.mention}'s balance: {bal} coin")
            else:
                await ctx.send(f"{ctx.author.mention}'s balance: {bal} coins")

    # .balance add <user_id> <amount>
    @balance.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, member: discord.Member, amount: int):
        guild_id = ctx.guild.id
        user = database.users.find_one({'user_id': member.id, 'guild_id': guild_id})

        if amount < 1:
            await ctx.send("`Amount value must be positive!`")
        else:
            if not user:
                user_services.create_user(member.id, guild_id)
                database.users.update_one({'user_id': member.id, 'guild_id': guild_id}, {'$set': {'balance': amount}})
            elif not user.get('balance'):
                database.users.update_one({'user_id': member.id, 'guild_id': guild_id}, {'$set': {'balance': amount}})
            else:
                database.users.update_one({'user_id': member.id, 'guild_id': guild_id}, {'$inc': {'balance': amount}})

            print(f'Balance of user with id {member.id} has been increase with {amount} coins')

    # error handling for .balance add <user_id> <amount>
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('`User is invalid or amount must be a positive integer!`')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("`Command must look like .balance add <user> <amount>`")

    # .daily for receive your daily coins
    @commands.command(name='daily', aliases=['d'], help='Claim your daily reward')
    async def daily_redeem(self, ctx):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        current_time = datetime.datetime.now()

        daily_bonus = database.guilds.find_one({'guild_id': guild_id}).get('daily_bonus')
        user = database.users.find_one({'user_id': user_id, 'guild_id': guild_id})

        if not user:
            user_services.create_user(user_id, guild_id)

        # if user doesn't exist user.get will throw AttributeError
        try:
            next_daily = user.get('next_daily')
        except AttributeError:
            next_daily = None

        if not next_daily or next_daily < current_time:
            tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
            next_daily = datetime.datetime.combine(tomorrow_date, datetime.time()) - datetime.timedelta(hours=3)

            database.users.update_one({'user_id': user_id, 'guild_id': guild_id},
                                      {'$set': {'next_daily': next_daily},
                                       '$inc': {'balance': daily_bonus}})
            await ctx.send(f'{ctx.author.mention}, you received {daily_bonus} coins!')
        else:
            time_difference = (next_daily - current_time).total_seconds()
            hours = int(time_difference / 3600)
            minutes = int(time_difference % 3600 / 60)
            await ctx.send(f'{ctx.author.mention}, your next daily is in {hours}h and {minutes}m!')


def setup(bot):
    bot.add_cog(User(bot))