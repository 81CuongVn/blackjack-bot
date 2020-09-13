import random

from discord.ext import commands
import discord
from helpers import user_services
from custom_errors import InsufficientFunds, MinimumBet
import asyncio
import random
from config import database


class Versus(commands.Cog):
    """
    Use command `versus <user> <bet>` to try your luck in a coinflip game with another person!
    """

    def __init__(self, bot):
        self.bot = bot
        self.versus_1_v_1 = {}

    # check if enemy react positive or negative for 1v1 coinflip match
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        guild_id = reaction.message.guild.id
        channel = reaction.message.channel
        if not self.versus_1_v_1.get(guild_id):
            self.versus_1_v_1[guild_id] = {}

        if reaction.message.id in self.versus_1_v_1[guild_id]:
            info = self.versus_1_v_1[guild_id][reaction.message.id]
            if user.id == info[1].id:
                if reaction.emoji == "✅":
                    player_2_bal = user_services.get_user_balance(info[1].id, guild_id)
                    player_1_bal = user_services.get_user_balance(info[0].id, guild_id)
                    bet = info[2]

                    await reaction.message.delete()

                    if player_1_bal < bet:
                        await channel.send(f'`{info[0].mention} has insufficient funds!`')
                    elif player_2_bal < bet:
                        await channel.send(f'`{info[1].mention} has insufficient funds!`')
                    else:
                        if random.randint(0, 1):
                            database.users.update_one({'user_id': info[0].id, 'guild_id': guild_id},
                                                      {'$inc': {'balance': bet}})
                            database.users.update_one({'user_id': info[1].id, 'guild_id': guild_id},
                                                      {'$inc': {'balance': -bet}})
                            await channel.send(f'{info[0].mention} won {bet} coins!')
                        else:
                            database.users.update_one({'user_id': info[0].id, 'guild_id': guild_id},
                                                      {'$inc': {'balance': -bet}})
                            database.users.update_one({'user_id': info[1].id, 'guild_id': guild_id},
                                                      {'$inc': {'balance': bet}})
                            await channel.send(f'{info[1].mention} won {bet} coins!')

                elif reaction.emoji == "❎":
                    await reaction.message.delete()

    # Coinflip versus another player !versus <user> <bet>, you have 50% to win or lose
    @commands.command(name='1v1')
    async def versus1v1(self, ctx, player_2: discord.Member, bet):
        if ctx.author != player_2:
            guild_id = ctx.guild.id
            player_1_id = ctx.author.id
            player_2_id = player_2.id

            player_2_bal = user_services.get_user_balance(player_2_id, guild_id)
            player_1_bal = user_services.get_user_balance(player_1_id, guild_id)
            minimum_bet = 1

            if not self.versus_1_v_1.get(guild_id):
                self.versus_1_v_1[guild_id] = {}

            if bet == 'all':
                bet = player_1_bal
            else:
                try:
                    bet = int(bet)
                except ValueError:
                    raise commands.UserInputError

            if bet < minimum_bet:
                raise MinimumBet(minimum_bet)
            elif player_1_bal < bet:
                raise InsufficientFunds
            elif player_2_bal < bet:
                await ctx.send('`Enemy has insufficient funds!`')
            else:
                message = await ctx.send(f"{player_2.mention} do you want to do a coinflip with {ctx.author.mention} for {bet} coins?")
                await message.add_reaction("✅")
                await message.add_reaction("❎")
                self.versus_1_v_1[guild_id][message.id] = [ctx.author, player_2, bet]

                await asyncio.sleep(60)
                await message.delete()
                if self.versus_1_v_1[guild_id].get(message.id):
                    del message.id
        else:
            await ctx.send('`Enemy must be another user!`')

    # Error handling for 1v1
    @versus1v1.error
    async def coinflip_error(self, ctx, error):
        if isinstance(error, MinimumBet):
            await ctx.send(f'`The minimum bet is {error.minimum_bet} coin!`')
        elif isinstance(error, InsufficientFunds):
            await ctx.send('`You have insufficient funds!`')
        elif isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'bet':
                await ctx.send("`You must enter a bet!`")
        elif isinstance(error, commands.UserInputError):
            await ctx.send("`User is invalid or amount must be a positive integer or all!`")


def setup(bot):
    bot.add_cog(Versus(bot))