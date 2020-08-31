import discord
from discord.ext import commands
from config import database


class Settings(commands.Cog):

    def __init__(self):
        pass

    # .settings - Shows current settings
    @commands.group(name='settings', help='Shows current settings')
    async def settings(self, ctx):
        if ctx.invoked_subcommand is None:
            guild_id = ctx.guild.id

            guild = database.guilds.find_one({'guild_id': guild_id})

            embed = discord.Embed(title='Blackjack-Bot Settings',
                                  description='`Use the command format .settings <option> to set something.`')
            embed.add_field(name='Blackjack minimum bet', value=f'{guild.get("minimum_bet_blackjack"):,}', inline=True)
            embed.add_field(name='Coinflip minimum bet', value=f"{guild.get('minimum_bet_coinflip'):,}", inline=True)
            embed.add_field(name='Daily bonus', value=f"{guild.get('daily_bonus'):,}", inline=True)

            await ctx.send(embed=embed)

    # .settings minimum_bet_blackjack <new_minimum_bet: int> - set new minimum bet to blackjack
    @settings.command()
    @commands.has_permissions(administrator=True)
    async def minimum_bet_blackjack(self, ctx, new_bet: int):
        guild_id = ctx.guild.id
        database.guilds.update_one({'guild_id': guild_id}, {'$set': {'minimum_bet_blackjack': new_bet}})

    # .settings minimum_bet_coinflip <new_minimum_bet: int> - set new minimum bet to coinflip
    @settings.command()
    @commands.has_permissions(administrator=True)
    async def minimum_bet_coinflip(self, ctx, new_bet: int):
        guild_id = ctx.guild.id
        database.guilds.update_one({'guild_id': guild_id}, {'$set': {'minimum_bet_coinflip': new_bet}})

    # .settings daily_bonus <new_daily_bonus: int> - set new daily bonus
    @settings.command()
    @commands.has_permissions(administrator=True)
    async def daily_bonus(self, ctx, new_daily_bonus: int):
        guild_id = ctx.guild.id
        database.guilds.update_one({'guild_id': guild_id}, {'$set': {'daily_bonus': new_daily_bonus}})

    # error handling for minimum_bet_blackjack
    @minimum_bet_blackjack.error
    async def minimum_bet_blackjack_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("`Command must look like .settings minimum_bet_blackjack <new_bet>`")
        elif isinstance(error, commands.UserInputError):
            await ctx.send("`New bet must be a integer!`")

    # error handling for minimum_bet_coinflip
    @minimum_bet_coinflip.error
    async def minimum_bet_coinflip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("`Command must look like .settings minimum_bet_coinflip <new_bet>`")
        elif isinstance(error, commands.UserInputError):
            await ctx.send("`New bet must be a integer!`")

    # error handling for daily_bonus
    @daily_bonus.error
    async def daily_bonus_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("`Command must look like .settings daily_bonus <new_daily_bonus>`")
        elif isinstance(error, commands.UserInputError):
            await ctx.send("`New daily bonus must be a integer!`")


def setup(bot):
    bot.add_cog(Settings())