import socket

class Player:
    def __init__(self, username: str, socket: socket.socket):
        self.username = username
        self.money = 500
        self.current_bet = 0
        self.hand = []
        self.isInGame = False
        self.standing = False
        self.has_doubled = False
        self.socket = socket

    def place_bet(self, amount: int, min_bet=10) -> bool:
        if self.current_bet > 0:
            return False
        if amount > self.money or amount < min_bet:
            return False
        self.current_bet = amount
        self.money -= amount
        return True

    def double_bet(self):
        if self.money >= self.current_bet and len(self.hand) == 2:
            self.money -= self.current_bet
            self.current_bet *= 2
            self.has_doubled = True
        else:
            raise ValueError("Cannot double down")