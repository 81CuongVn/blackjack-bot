import discord
import pymongo
from PIL import Image, ImageDraw, ImageFont

from config import database, bot, token


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


# Shows top 5 balance on the server
@bot.command(name='top', help='Shows top 5 balances on the server')
async def top(ctx):
    guild_id = ctx.guild.id
    top_users = {}
    max_len_name = 0
    max_len_balance = 0

    users = database.users.find({'guild_id': guild_id}).sort('balance', pymongo.DESCENDING).limit(5)
    for user in users:
        name = ctx.guild.get_member(user.get("user_id")).display_name
        user_balance = str(user.get("balance"))
        top_users[name] = str(user.get("balance"))
        if len(name) > max_len_name:
            max_len_name = len(name)
        if len(user_balance) > max_len_balance:
            max_len_balance = len(user_balance)

    top_len = 16 + max_len_name + max_len_balance

    top_str = f'Top balance on server - {ctx.guild.name}\n\n'
    if len(top_str) > top_len:
        top_len = len(top_str)

    for idx, (name, user_balance) in enumerate(top_users.items(), start=1):
        top_str += f'{idx}. {name.ljust(max_len_name)} - balance: {user_balance.rjust(max_len_balance)}\n'

    img = Image.new('RGBA', (top_len*35, 365), color=(255, 0, 0, 0))
    fnt = ImageFont.truetype('assets/consolab.ttf', 60)
    d = ImageDraw.Draw(img)
    d.text((10, 10), top_str, font=fnt, fill=(235, 89, 61))

    img.save('top.png')
    await ctx.send(file=discord.File('top.png'))


bot.load_extension('cogs.settings')
bot.load_extension('cogs.blackjack')
bot.load_extension('cogs.coinflip')
bot.load_extension('cogs.versus')
bot.load_extension('cogs.user')

bot.run(token)
