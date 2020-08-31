import pymongo
import datetime

from discord.ext import commands
from config import database, bot, token
from helpers import user_services


# if blackjack bot is removed from a server he deletes server settings
@bot.listen()
async def on_guild_remove(guild):
    guild_id = guild.id
    database.guilds.delete_one({'guild_id': guild_id})


# if blackjack bot joins a server he make default settings for it
@bot.listen()
async def on_guild_join(guild):
    guild_id = guild.id
    database.guilds.insert_one({
        'guild_id': guild_id,
        'minimum_bet_blackjack': 200,
        'minimum_bet_coinflip': 100,
        'daily_bonus': 10_000})


# if a user joins a server blackjack-bot creates a entry in database
@bot.listen()
async def on_member_join(member):
    guild_id = member.guild.id
    member_id = member.id
    database.users.insert_one({'user_id': member_id, 'balance': 0, 'guild_id': guild_id})


# if a user left a server blackjack-bot delete his entry in database
@bot.listen()
async def on_member_remove(member):
    guild_id = member.guild.id
    member_id = member.id
    database.users.delete_one({'user_id': member_id, 'guild_id': guild_id})


# .balance - show a user balance
@bot.group(name='balance', aliases=['b', 'bal'], help='Shows your balance')
async def balance(ctx):
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
async def add(ctx, user_id: int, amount: int):
    user = database.users.find_one({'user_id': user_id})
    guild_id = ctx.guild.id

    if not user:
        await ctx.send("`User id it's not valid!`")
    elif not user.get('balance'):
        database.users.update_one({'user_id': user_id, 'guild_id': guild_id}, {'$set': {'balance': amount}})
    else:
        database.users.update_one({'user_id': user_id, 'guild_id': guild_id}, {'$inc': {'balance': amount}})

    print(f'Balance of user with id {user_id} has been increase with {amount} coins')


# Shows top 5 balance on the server
@bot.command(name='top', help='Shows top 5 balances on the server')
async def top(ctx):
    guild_id = ctx.guild.id
    top_string = ""

    users = database.users.find({'guild_id': guild_id}).sort('balance', pymongo.DESCENDING).limit(5)
    for idx, user in enumerate(users, start=1):
        name = ctx.guild.get_member(user.get("user_id")).display_name
        name_string = name.center(32, ' ')
        top_string += f'{idx}. {name_string} - balance: {user.get("balance")} coins \n'

    top_string = "```" + top_string + "```"
    await ctx.send(top_string)


# .daily for receive your daily coins
@bot.command(name='daily', aliases=['d'], help='Claim your daily reward')
async def daily_redeem(ctx):
    guild_id = ctx.guild.id
    user_id = ctx.author.id
    current_time = datetime.datetime.now()

    daily_bonus = database.guilds.find_one({'guild_id': guild_id}).get('daily_bonus')
    user = database.users.find_one({'user_id': user_id, 'guild_id': guild_id})

    if not user:
        database.users.insert_one({'user_id': user_id, 'balance': 0, 'guild_id': guild_id})

    next_daily = user.get('next_daily')

    if not next_daily or next_daily < current_time:
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        next_daily = datetime.datetime.combine(tomorrow_date, datetime.time())

        database.users.update_one({'user_id': user_id, 'guild_id': guild_id},
                                  {'$set': {'next_daily': next_daily},
                                   '$inc': {'balance': daily_bonus}})
        await ctx.send(f'{ctx.author.mention}, you received {daily_bonus} coins!')
    else:
        time_difference = (next_daily - current_time).total_seconds()
        hours = int(time_difference / 3600)
        minutes = int(time_difference % 3600 / 60)
        await ctx.send(f'{ctx.author.mention}, your next daily is in {hours}h and {minutes}m!')


# error handling for .balance add <user_id> <amount>
@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("`Command must look like .balance add <user_id> <amount>`")
    elif isinstance(error, commands.UserInputError):
        await ctx.send("`User id and amount must be both integers!`")


bot.load_extension('cogs.settings')
bot.load_extension('cogs.blackjack')
bot.load_extension('cogs.coinflip')

bot.run(token)
