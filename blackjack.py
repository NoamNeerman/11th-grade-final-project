import random
import socket

from pClass import Player as pl
class blackjack_game:
    def __init__(self) -> None:
        self.deck = [2,3,4,5,6,7,8,9,10,'J','Q','K','A'] * 4
        self.players = []
        self.dealer = []
        self.current_phase = "betting"  # betting -> dealing -> player_turns -> dealer_turn -> payout
        self.current_player_idx = 0
        self.shuffleDeck()

    def joinGame(self, player: pl) ->None:
        self.players.append(player)
        player.isInGame = True

    def advance_phase(self) -> None:
        phases = ["betting", "dealing", "player_turns", "dealer_turn", "payout"]
        current_idx = phases.index(self.current_phase)
        self.current_phase = phases[(current_idx + 1) % 5]

        if self.current_phase == "player_turns":
            self.current_player_idx = 0
        elif self.current_phase == "dealing":
            self.firstDeal()
            self.current_phase = "player_turns"


    def get_current_player(self)->pl:
        if self.current_phase == "player_turns":
            return self.players[self.current_player_idx]
        return None


    def next_player(self)->None:
        self.current_player_idx += 1
        if self.current_player_idx >= len(self.players):
            self.advance_phase()  # Move to dealer turn


    def sumHand(self, hand: list) -> int:
        total = 0
        aces = 0
        for card in hand:
            if card in ['J', 'Q', 'K']:
                total += 10
            elif card == 'A':
                aces += 1
            else:
                total += card

        for _ in range(aces):
            if total + 11 > 21:
                total += 1
            else:
                total += 11

        return total


    def shuffleDeck(self) ->None:
        random.shuffle(self.deck)


    def __drawCard(self):
        if not self.deck:
            self.deck = [2,3,4,5,6,7,8,9,10,'J','Q','K','A'] * 4
            self.shuffleDeck()
        return self.deck.pop()


    def firstDeal(self)->None:
        """Gives two cards to each player and the dealer"""
        for _ in range(2):  # Give two cards each
            self.dealer.append(self.__drawCard())
            for p in self.players:
                p.hand.append(self.__drawCard())
                if self.sumHand(p.hand) == 21:
                    self.stand(p)
                    self.next_player()


    def deal(self, player: pl) -> bool:
        if self.current_phase != "player_turns":
            raise ValueError("Not the right phase for dealing")

        player.hand.append(self.__drawCard())
        total = self.sumHand(player.hand)

        if total > 21:
            player.isInGame = False
            self.next_player()
        elif total == 21:
            self.stand(player)
            self.next_player()
        return True


    def stand(self, player: pl) ->bool:
        player.standing = True
        return True

    def dealer_turn(self) -> bool:
        if all(p.standing or not p.isInGame for p in self.players):
            while self.sumHand(self.dealer) < 17:
                self.dealer.append(self.__drawCard())
            self.advance_phase()
            return True
        return False

    def double_down(self, player: pl)->bool:
            if len(player.hand) == 2 and player.money >= player.current_bet:
                    player.money -= player.current_bet
                    player.current_bet *= 2
                    self.deal(player)
                    self.stand(player)
                    self.next_player()
            return True

    def winOrNo(self, player: pl) -> bool:
        p_sum = self.sumHand(player.hand)
        d_sum = self.sumHand(self.dealer)

        if not player.isInGame:  # Player busted
            return False

        p_blackjack = p_sum == 21 and len(player.hand) == 2
        d_blackjack = d_sum == 21 and len(self.dealer) == 2

        if p_blackjack and not d_blackjack:
            player.money += player.current_bet * 2.5
            return True
        elif p_blackjack and d_blackjack:
            player.money += player.current_bet  # Push
            return False
        elif not p_blackjack and d_blackjack:
            return False

        # Regular outcomes
        if p_sum > 21:
            return False
        elif d_sum > 21:
            player.money += player.current_bet * 2
            return True
        elif p_sum > d_sum:
            player.money += player.current_bet * 2
            return True
        elif p_sum == d_sum:
            player.money += player.current_bet  # Push
            return False
        else:
            return False

    def is_round_complete(self)->bool:
        return self.current_phase == "payout"

    def getGameState(self) -> dict:
        return {
            "dealer": {
                "cards": [str(card) for card in self.dealer] if self.current_phase in ("payout", "betting")
                else [str(self.dealer[0])] + ['?' for _ in range(len(self.dealer) - 1)]
            },
            "players": [
                {
                    "username": p.username,
                    "hand": [str(card) for card in p.hand],
                    "money": p.money,
                    "isInGame": p.isInGame,
                    "standing": p.standing,
                    "current_bet": p.current_bet
                }
                for p in self.players
            ],
            "current_phase": self.current_phase,
            "current_player": self.players[
                self.current_player_idx].username if self.current_phase == "player_turns" else None
        }


    def getWinners(self) ->list:
        return [p for p in self.players if self.winOrNo(p)]


    def resetGame(self)->None:
        self.dealer = []
        self.deck = [2,3,4,5,6,7,8,9,10,'J','Q','K','A'] * 4
        self.shuffleDeck()
        for p in self.players:
            p.hand = []
            p.standing = False
            p.isInGame = True
            p.current_bet = 0
            p.has_doubled = False
        self.current_player_idx = 0
        self.current_phase = "betting"




















