
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
import threading
import socket
import json

Window.size = (800, 600)

class BlackjackClientUI(App):
    def build(self):
        self.sock = None
        self.username = ""

        self.root_layout = BoxLayout(orientation='vertical')
        self.join_screen()
        return self.root_layout

    def join_screen(self):
        self.root_layout.clear_widgets()

        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text='Enter Your Name', font_size=24))

        self.name_input = TextInput(hint_text='Your Name', multiline=False, size_hint=(1, 0.2))
        box.add_widget(self.name_input)

        join_button = Button(text='Join', size_hint=(1, 0.2))
        join_button.bind(on_press=self.join_game)
        box.add_widget(join_button)

        self.root_layout.add_widget(box)

    def join_game(self, instance):
        self.username = self.name_input.text.strip()
        if not self.username:
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 63))
            self.send("join", {"username": self.username})

            threading.Thread(target=self.receive_loop, daemon=True).start()
            self.game_screen()
        except Exception as e:
            self.show_popup("Connection Error", str(e))

    def game_screen(self):
        self.root_layout.clear_widgets()

        self.table = GridLayout(cols=1, padding=10, spacing=10)

        self.players_display = Label(text="Waiting for game state...", font_size=18, markup=True)
        self.table.add_widget(self.players_display)

        actions = BoxLayout(size_hint=(1, 0.2), spacing=5)
        for action in ["hit", "stand", "double"]:
            btn = Button(text=action)
            btn.bind(on_press=self.send_action)
            actions.add_widget(btn)
        self.table.add_widget(actions)

        bet_box = BoxLayout(size_hint=(1, 0.2), spacing=5)

        # Create input first before adding it
        self.bet_input = TextInput(hint_text="Bet Amount", multiline=False)
        bet_box.add_widget(self.bet_input)

        self.place_bet_button = Button(text="Place Bet")
        self.place_bet_button.bind(on_press=self.place_bet)
        bet_box.add_widget(self.place_bet_button)

        self.table.add_widget(bet_box)

        self.root_layout.add_widget(self.table)

    def place_bet(self, instance):
        try:
            amount = int(self.bet_input.text)
            self.send("bet", {"amount": amount})
            self.place_bet_button.disabled = True  # Disable after placing the bet
        except ValueError:
            self.show_popup("Invalid Input", "Please enter a valid number.")

    def send_action(self, instance):
        action = instance.text.lower()
        self.send(action, {})

    def send(self, status, data):
        try:
            msg = json.dumps({"status": status, "data": data})
            self.sock.send(msg.encode())
        except:
            self.show_popup("Error", "Failed to send message.")

    def receive_loop(self):
        while True:
            try:
                raw = self.sock.recv(4096).decode()
                if not raw:
                    break
                msg = json.loads(raw)
                Clock.schedule_once(lambda dt: self.handle_message(msg))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_popup("Connection Lost", str(e)))
                break

    def handle_message(self, msg):
        status = msg['status']
        data = msg['data']
        print(status)
        if status == "update":
            self.update_game_state(data)
        elif status == "error":
            self.show_popup("Server Error", data)
        elif status == "reset":
            if hasattr(self,'place_bet_button'):
                self.place_bet_button.disabled = False
        elif status == "round_end":
            self.show_popup("Round Result", f"You {data}!")

    def update_game_state(self, state):
        display = "\n[Blackjack Table]\n"
        for player in state.get("players", []):
            cards = " , ".join(player.get("hand"))
            print(player)
            name = player['username']
            if name == self.username:
                name = f"[color=00ffff]{name}[/color]"
            display += f"Player: {name}  💰${player['money']}   {cards}  Standing: {player['standing']}\n"

        dealer_cards = state.get("dealer", {}).get("cards", ["🃏"])
        display += f"Dealer: {' '.join(dealer_cards)}\n"
        self.players_display.text = display

    def show_popup(self, title, message):
        label = Label(text=message)
        popup = Popup(title=title,
                      content=label,
                      size_hint=(0.6, 0.4),
                      auto_dismiss=True)
        popup.open()


if __name__ == '__main__':
    BlackjackClientUI().run()
