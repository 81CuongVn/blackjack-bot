import copy
import random

import discord

from config import database


class BlackJackGame:
    def __init__(self, bet: int, player_name: str, player_id: int, player_cards: list, dealer_cards: list,
                 game_pack: list):
        # Decrease player balance with his bet
        database.users.update_one({'user_id': player_id}, {'$inc': {'balance': -bet}})

        # Initial settings for a blackjack game
        # Player's bet
        self.bet = bet

        # Player info
        self.player_name = player_name
        self.player_id = player_id
        self.player_cards = player_cards
        self.player_total = 0
        self.player_a_number = 0

        # Dealer info
        self.dealer_cards = dealer_cards
        self.dealer_total_showed = '?'
        self.dealer_total = 0
        self.dealer_a_number = 0

        # Game title and status
        self.title = f"**{self.player_name}**'s game ({self.bet} coins)"
        self.status = 'in game'

        # Copy and shuffle standard 52 cards deck
        self.game_pack = copy.deepcopy(game_pack)
        random.shuffle(self.game_pack)

        # Draw first 2 cards for player
        for i in range(2):
            card = self.game_pack.pop()
            # Change one of 'A' points to 1 if both first cards are 'A'
            if card.number == 'A' and self.player_total == 11:
                self.player_total += 1
                card.number = '1'
            else:
                self.player_total += card.points
            self.player_cards.append(card)
            if card.number == 'A':
                self.player_a_number += 1

        # Draw first 2 cards for dealer
        # Draw the hidden card for dealer
        secret_card = self.game_pack.pop()
        secret_card.symbol = '`?`'
        self.dealer_total += secret_card.points
        dealer_cards.append(secret_card)
        if secret_card.number == 'A':
            self.dealer_a_number += 1

        # Draw the showed card for dealer
        card = self.game_pack.pop()
        # Change one of 'A' points to 1 if both first cards are 'A'
        if card.number == 'A' and self.dealer_total == 11:
            self.dealer_total += 1
            card.number = '1'
        else:
            self.dealer_total += card.points
        dealer_cards.append(card)
        if card.number == 'A':
            self.dealer_a_number += 1

        if self.player_total == self.dealer_total == 21:
            self.draw_event()
        elif self.player_total == 21:
            self.blackjack_event_player()
        elif self.dealer_total == 21:
            self.blackjack_event_dealer()

    # FOR DEALER
    # Verify if exist and change "A" card value if the value of points it's over 21,
    # if "A" card exist and changed value it's less than 22 return True, otherwise return False
    def change_a_value_dealer(self) -> bool:
        for card in self.dealer_cards:
            if card.number == 'A':
                self.dealer_total -= 10
                card.number = '1'
            if self.dealer_total <= 21:
                return True
        return False

    # FOR PLAYER
    # Verify if exist and change "A" card value if the value of points it's over 21,
    # if "A" card exist and changed value it's less than 22 return True, otherwise return False
    def change_a_value_player(self) -> bool:
        for card in self.player_cards:
            if card.number == 'A':
                self.player_total -= 10
                card.number = '1'
            if self.player_total <= 21:
                return True
        return False

    # Create the representation of blackjack game in a embed
    def embed(self):
        embed = discord.Embed(title=self.title,
                              description='`!hit | !stand | !double | !surrender`')
        embed.add_field(name='**You**', value=self.player_info(), inline=True)
        embed.add_field(name='**Dealer**', value=self.dealer_info(), inline=True)
        embed.set_footer(text='Game mode: Blackjack')
        return embed

    # Return a string with player's cards and total of points
    def player_info(self):
        var = []
        for i in self.player_cards:
            var.append(i.symbol)
        return ' '.join(var) + '\n' + f'**Total: {self.player_total}**'

    # Return a string with dealer's cards and total of points
    def dealer_info(self):
        var = []
        for i in self.dealer_cards:
            var.append(i.symbol)
        return ' '.join(var) + '\n' + f'**Total: {self.dealer_total_showed}**'

    # Show dealer's hidden card and total of points
    def dealer_final_show(self):
        secret_card = self.dealer_cards[0]
        if secret_card.number == '1':
            secret_card.number = 'A'
        secret_card.symbol = '`' + secret_card.number + secret_card.card_type + '`'
        self.dealer_cards[0] = secret_card
        self.dealer_total_showed = self.dealer_total

    # Action of hit a card in blackjack
    def hit_a_card(self):
        card = self.game_pack.pop()
        self.player_cards.append(card)
        self.player_total += card.points
        if self.player_total > 21:
            if not self.change_a_value_player():
                self.lose_event()
        elif self.player_total == 21:
            self.stand()

    # Action of stand in blackjack
    def stand(self):
        while self.dealer_total < 17:
            card = self.game_pack.pop()
            self.dealer_cards.append(card)
            self.dealer_total += card.points
            if self.dealer_total > 21:
                self.change_a_value_dealer()

        if self.dealer_total > 21 or self.dealer_total < self.player_total:
            self.win_event()
        elif self.dealer_total > self.player_total:
            self.lose_event()
        else:
            self.draw_event()

    # Action of double in blackjack
    def double(self):
        database.users.update_one({'user_id': self.player_id}, {'$inc': {'balance': -self.bet}})
        self.bet *= 2
        card = self.game_pack.pop()
        self.player_cards.append(card)
        self.player_total += card.points
        if self.player_total > 21:
            if not self.change_a_value_player():
                self.lose_event()
                return
        self.stand()

    # When player have blackjack
    def blackjack_event_dealer(self):
        self.title = f"Dealer blackjack - **{self.player_name}** lost {self.bet} coins"
        self.status = 'finished'
        self.dealer_final_show()

    # When player have blackjack
    def blackjack_event_player(self):
        # Increase player balance with bet * 2.5 if he hit blackjack
        database.users.update_one({'user_id': self.player_id}, {'$inc': {'balance': int(self.bet * 2.5)}})

        # Change title and end the game
        self.title = f"Blackjack - **{self.player_name}** won {int(self.bet * 1.5)} coins"
        self.status = 'finished'
        self.dealer_final_show()

    # Classic win in blackjack
    def win_event(self):
        # Increase player balance with bet * 2 if he win
        database.users.update_one({'user_id': self.player_id}, {'$inc': {'balance': int(self.bet * 2)}})

        # Change title and end the game
        self.title = f"Win - **{self.player_name}** won {self.bet} coins"
        self.status = 'finished'
        self.dealer_final_show()
        # update player bal

    # Lose in blackjack
    def lose_event(self):
        # Change title and end the game
        self.title = f"Lose - **{self.player_name}** lost {self.bet} coins"
        self.status = 'finished'
        self.dealer_final_show()

    # Draw in blackjack
    def draw_event(self):
        # Refund player's coins if he draw
        database.users.update_one({'user_id': self.player_id}, {'$inc': {'balance': int(self.bet)}})

        # Change title and end the game
        self.title = f"Draw - **{self.player_name}** won 0 coins"
        self.status = 'finished'
        self.dealer_final_show()
