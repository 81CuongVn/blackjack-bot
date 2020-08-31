import os

import pymongo
from discord.ext import commands

# token for bot
token = os.environ['bot-token']

# setup command prefix
command_prefix = os.environ['bot-command-prefix']
bot = commands.Bot(command_prefix=command_prefix)

# setup database
conn_str = os.environ['conn-str']
cluster_name = os.environ['cluster-name']

# Connect to cluster
cluster = pymongo.MongoClient(conn_str)
# Connect to database
database = cluster[cluster_name]