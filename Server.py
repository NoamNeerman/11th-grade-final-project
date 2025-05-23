import socket
import json
import time

from blackjack import blackjack_game
from pClass import Player
import threading

HOST = '127.0.0.1'
PORT = 63

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

game = blackjack_game()

#"""update function to send to all clients. That's an easy way for me to transfer data across clients"""
def broadcast_game_state():
    state = json.dumps({"status": "update", "data": game.getGameState()})
    for p in game.players:
        try:
            p.socket.sendall(state.encode())
        except:
            game.players.remove(p)

#A separate thread to check for some game state changes
def game_manager_loop():
    while True:
        if game.current_phase == "dealer_turn":
            if game.dealer_turn():
                broadcast_game_state()
        elif game.is_round_complete():
                winners = game.getWinners()
                for player in game.players:
                    try:
                        player.socket.send(json.dumps({
                            "status": "round_end",
                            "data": "won!" if player in winners else "didn't win"
                        }).encode())
                    except:
                        pass

                time.sleep(1)
                game.resetGame()
                for p in game.players:
                    try:
                        p.socket.sendall(json.dumps({
                            "status": "reset",
                            "data": {"message": ""}
                        }).encode())
                    except:
                        game.players.remove(p)

                time.sleep(0.1)  # Small delay before broadcasting new state
                broadcast_game_state()
        time.sleep(1)


def handle_client(conn: socket.socket, addr: tuple):
    try:
        raw = conn.recv(1024).decode()
        msg = json.loads(raw)

        if msg["status"] == "join":
            if game.current_phase != "betting":
                # Reject connection if game is in progress
                conn.send(json.dumps({"status": "error", "data": "Game in progress. Try again later."}).encode())
                conn.close()
                return

            username = msg["data"]["username"]
            player = Player(username, conn)
            game.joinGame(player)
            print(f"{username} joined from {addr}")
            broadcast_game_state()

        else:
            conn.close()
            return

        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            msg = json.loads(data)

            player: Player = next((p for p in game.players if p.socket == conn), None)
            if not player:
                continue

            status = msg["status"]
            info = msg["data"]
            if status == "bet":
                if player.place_bet(info["amount"]):
                    broadcast_game_state()
                elif player.current_bet != 0:
                    conn.send(json.dumps({"status": "error", "data": "Cannot bet twice!"}).encode())
                else:
                    conn.send(json.dumps({"status": "error", "data": "Invalid bet amount!"}).encode())
                if all(p.current_bet > 0 for p in game.players):
                    game.advance_phase()
                    broadcast_game_state()

            elif status == "hit":
                if game.get_current_player() == player:
                    game.deal(player)
                    broadcast_game_state()
                else:
                    conn.send(json.dumps({"status": "error", "data": "Can't hit right now. Please wait."}).encode())

            elif status == "stand":
                if game.get_current_player() == player:
                    success = game.stand(player)
                    if success:
                        game.next_player()
                        broadcast_game_state()
                else:
                    conn.send(json.dumps({"status": "error", "data": "Cannot stand right now. Please wait"}).encode())

            elif status == "double":
                if game.get_current_player() == player:
                    success = game.double_down(player)
                    if success:
                        broadcast_game_state()
                else:
                    conn.send(json.dumps({"status": "error", "data": "This is not your turn. Please wait"}).encode())



    except Exception as e:
        print("Client error:", e)
        conn.close()

def accept_clients():
    print("Server started...")
    while True:
        conn, addr = server.accept()
        if len(game.players) >=4:
            conn.send(json.dumps({"status": "error", "data": "Game is full. Please try again later."}).encode())
            conn.close()
            continue
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

threading.Thread(target=game_manager_loop,daemon=True).start()
accept_clients()
