from discord.ext import commands

from config import bot, token
from config import database
from helpers import user_services


# !balance - show a user balance
@bot.group(name='balance', aliases=['b', 'bal'], help='Shows your balance')
async def balance(ctx):
    if ctx.invoked_subcommand is None:
        user_id = ctx.author.id

        # Get user's balance
        bal = user_services.get_user_balance(user_id)

        if bal == 1:
            await ctx.send(f"{ctx.author.mention}'s balance: {bal} coin")
        else:
            await ctx.send(f"{ctx.author.mention}'s balance: {bal} coins")


# !balance add <user_id> <amount>
@balance.command()
@commands.has_permissions(administrator=True)
async def add(ctx, user_id: int, amount: int):
    user = database.users.find_one({'user_id': user_id})

    if not user:
        await ctx.send("`User id it's not valid!`")
    elif not user.get('balance'):
        database.users.update_one({'user_id': user_id}, {'$set': {'balance': amount}})
    else:
        database.users.update_one({'user_id': user_id}, {'$inc': {'balance': amount}})

    print(f'Balance of user with id {user_id} has been increase with {amount} coins')


# error handling for !balance add
@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("`Command must look like !balance add <user_id> <amount>`")
    elif isinstance(error, commands.UserInputError):
        await ctx.send("`User id and amount must be both integers!`")


# Disconnect bot
@bot.command(name='bye')
@commands.has_permissions(administrator=True)
async def disconnect(ctx):
    await ctx.send("Goodbye!")
    await bot.close()


bot.load_extension('cogs.blackjack')

bot.run(token)
