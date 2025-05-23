import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

# Card values
CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# Deck of cards
DECK = [f"{rank}♥" for rank in CARD_VALUES] + [f"{rank}♦" for rank in CARD_VALUES] + \
       [f"{rank}♠" for rank in CARD_VALUES] + [f"{rank}♣" for rank in CARD_VALUES]


class BlackjackGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, **kwargs)
        self.deck = DECK.copy()
        random.shuffle(self.deck)

        self.player_hand = []
        self.dealer_hand = []

        self.label = Label(text="Welcome to Blackjack!", font_size="24sp", color=[1, 0, 0, 1])  # Red text
        self.add_widget(self.label)

        self.hit_button = Button(text="Hit", font_size="20sp", background_color=[0, 0, 0, 1], color=[1, 1, 1, 1])
        self.hit_button.bind(on_press=self.hit)
        self.add_widget(self.hit_button)

        self.stand_button = Button(text="Stand", font_size="20sp", background_color=[1, 0, 0, 1], color=[1, 1, 1, 1])
        self.stand_button.bind(on_press=self.stand)
        self.add_widget(self.stand_button)

        self.deal_button = Button(text="Deal", font_size="20sp", background_color=[0, 0, 0, 1], color=[1, 1, 1, 1])
        self.deal_button.bind(on_press=self.deal)
        self.add_widget(self.deal_button)

    def deal(self, instance):
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop()]
        self.update_label()

    def hit(self, instance):
        self.player_hand.append(self.deck.pop())
        if self.get_hand_value(self.player_hand) > 21:
            self.show_popup("Bust! You lose!")
        self.update_label()

    def stand(self, instance):
        while self.get_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())

        if self.get_hand_value(self.dealer_hand) > 21 or self.get_hand_value(self.player_hand) > self.get_hand_value(self.dealer_hand):
            self.show_popup("You win!")
        else:
            self.show_popup("Dealer wins!")
        self.update_label()

    def get_hand_value(self, hand):
        value = sum(CARD_VALUES[card[:-1]] for card in hand)
        if value > 21 and any(card.startswith("A") for card in hand):
            value -= 10
        return value

    def update_label(self):
        self.label.text = f"Player: {' '.join(self.player_hand)}\nDealer: {' '.join(self.dealer_hand)}"

    def show_popup(self, message):
        popup = Popup(title="Game Over",
                      content=Label(text=message, font_size="20sp"),
                      size_hint=(None, None), size=(300, 200))
        popup.open()


class BlackjackApp(App):
    def build(self):
        return BlackjackGame()


if __name__ == "__main__":
    BlackjackApp().run()
