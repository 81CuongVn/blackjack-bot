import os

import pymongo
from discord.ext import commands

# token for bot
token = os.environ['BOT_TOKEN']

# setup command prefix
command_prefix = os.environ['BOT_COMMAND_PREFIX']
bot = commands.Bot(command_prefix=command_prefix)

# setup database
conn_str = os.environ['CONN_STR']
cluster_name = os.environ['CLUSTER_NAME']

# Connect to cluster
cluster = pymongo.MongoClient(conn_str)
# Connect to database
database = cluster[cluster_name]
