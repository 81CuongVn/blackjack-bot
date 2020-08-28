from config import database


# Return user's balance by user id from discord
def get_user_balance(user_id: int) -> int:
    # Search for user in database
    user = database.users.find_one({'user_id': user_id})

    # Get balance from user, if user's balance or user doesn't exist create a new user with balance 0
    if not user:
        database.users.insert_one({'user_id': user_id, 'balance': 0})
        return 0
    elif not user.get('balance'):
        database.users.update_one({'user_id': user_id}, {'$set': {'balance': 0}})
        return 0
    else:
        return user.get('balance')