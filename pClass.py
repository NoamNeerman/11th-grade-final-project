import socket

class Player:
    def __init__(self, username: str, player_socket: socket.socket):
        self.username = username
        self.cash = 500
        self.current_bet = 0
        self.hand = []
        self.isInGame = False
        self.standing = False
        self.has_doubled = False
        self.socket = player_socket

    def place_bet(self, amount: int, min_bet=10):
        if amount > self.cash:
            raise ValueError("Cannot bet more than available cash")
        if amount < min_bet:
            raise ValueError(f"Minimum bet is {min_bet}")
        self.current_bet = amount
        self.cash -= amount

    def double_bet(self):
        if self.cash >= self.current_bet and len(self.hand) == 2:
            self.cash -= self.current_bet
            self.current_bet *= 2
            self.has_doubled = True
        else:
            raise ValueError("Cannot double down")