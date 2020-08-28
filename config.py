import configparser

import pymongo
from discord.ext import commands

config = configparser.ConfigParser()
config.read('bot_config.ini')

# Minimum bet for blackjack
minimum_bet = int(config['blackjack']['minimum_bet'])

# token for bot
token = config['bot']['token']

# setup command prefix
command_prefix = config['bot']['command_prefix']
bot = commands.Bot(command_prefix=command_prefix)

# setup database
conn_str = config['database']['conn_str']
cluster_name = config['database']['cluster_name']

# Connect to cluster
cluster = pymongo.MongoClient(conn_str)
# Connect to database
database = cluster[cluster_name]
