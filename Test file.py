from pClass import Player
from blackjack import blackjack_game  # or whatever your blackjack game file is named

def main():
    game = blackjack_game()

    num_players = int(input("How many players? "))
    for i in range(num_players):
        username = input(f"Enter name for player {i + 1}: ")
        player = Player(username)
        game.joinGame(player)

    while True:
        print("\n--- New Round ---\n")
        game.resetGame()

        # Betting phase
        game.current_phase = "betting"
        for player in game.players:
            while True:
                try:
                    bet = int(input(f"{player.username}, you have ${player.cash}. Place your bet: "))
                    player.place_bet(bet)
                    break
                except ValueError as e:
                    print(e)

        # Dealing phase
        game.advance_phase()
        game.firstDeal()

        # Player turns
        game.advance_phase()
        while game.current_phase == "player_turns":
            player = game.get_current_player()
            if player.isInGame and not player.standing:
                print(f"\n{player.username}'s turn!")
                print(f"Your hand: {player.hand} (Total: {game.sumHand(player.hand)})")
                print(f"Dealer shows: {game.dealer[0]}")
                move = input("Choose action: (h)it, (s)tand, (d)ouble down: ").lower()

                if move == 'h':
                    game.deal(player)
                elif move == 's':
                    game.stand(player)
                    game.next_player()
                elif move == 'd':
                    try:
                        game.double_down(player)
                    except ValueError as e:
                        print(e)
                else:
                    print("Invalid choice, please pick again.")
            else:
                game.next_player()

        # Dealer's turn
        game.dealer_turn()
        print("\nDealer's hand:", game.dealer, "(Total:", game.sumHand(game.dealer), ")")

        # Payout phase
        game.advance_phase()
        print("\n--- Results ---")
        winners = game.getWinners()

        for p in game.players:
            status = "WON" if p.username in winners else "LOST"
            print(f"{p.username}: {status}, Cash: ${p.cash}")

        # Check if players want to continue
        cont = input("\nPlay another round? (y/n): ").lower()
        if cont != 'y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()
