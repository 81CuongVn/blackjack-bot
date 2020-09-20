from config import database


# Return user's balance by user id from discord
def get_user_balance(user_id: int, guild_id: int) -> int:
    # Search for user in database
    user = database.users.find_one({'user_id': user_id, 'guild_id': guild_id})

    # Get balance from user, if user's balance or user doesn't exist create a new user with balance 0
    if not user:
        create_user(user_id, guild_id)
        return 0
    elif not user.get('balance'):
        database.users.update_one({'user_id': user_id, 'guild_id': guild_id}, {'$set': {'balance': 0}})
        return 0
    else:
        return user.get('balance')


def create_user(user_id: int, guild_id: int):
    database.users.insert_one({'user_id': user_id,
                               'balance': 0,
                               'guild_id': guild_id,
                               'level': 0,
                               'experience': 0})