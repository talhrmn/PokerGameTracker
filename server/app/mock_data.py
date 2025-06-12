import random
from datetime import UTC, datetime, timedelta

from bson import ObjectId
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


# Generate test data
NUM_USERS = 10
NUM_TABLES = 5
PASSWORD = "123!@#qweQWE"
PASSWORD_HASH = get_password_hash(PASSWORD)
VENUES = ["Home Game", "Casino Royale", "The Poker Room", "Underground", "VIP Lounge"]
BLIND_STRUCTURES = ["1/2", "2/5", "5/10", "10/20", "25/50"]


def main():
    # Create users
    users = []
    for i in range(1, NUM_USERS + 1):
        user_id = ObjectId()
        username = f"user_{i}"
        email = f"user_{i}@gmail.com"

        total_profit = random.randint(-500, 2000)
        win_rate = random.uniform(0.3, 0.7)
        tables_played = random.randint(5, 50)
        hours_played = random.randint(20, 200)

        # Generate monthly stats
        monthly_stats = []
        months = [
            "Oct 2024",
            "Nov 2024",
            "Dec 2024",
            "Jan 2025",
            "Feb 2025",
            "Mar 2025",
        ]
        for month in months:
            monthly_profit = random.randint(-200, 500)
            monthly_win_rate = random.uniform(0.25, 0.75)
            monthly_tables = random.randint(1, 10)
            monthly_hours = random.randint(4, 40)

            monthly_stats.append(
                {
                    "month": month,
                    "profit": monthly_profit,
                    "win_rate": monthly_win_rate,
                    "tables_played": monthly_tables,
                    "hours_played": monthly_hours,
                }
            )

        user = {
            "_id": user_id,
            "username": username,
            "email": email,
            "password_hash": PASSWORD_HASH,
            "profile_pic": None,
            "created_at": datetime.now(UTC) - timedelta(days=random.randint(1, 365)),
            "last_login": datetime.now(UTC) - timedelta(days=random.randint(0, 30)),
            "stats": {
                "total_profit": total_profit,
                "win_rate": win_rate,
                "tables_played": tables_played,
                "hours_played": hours_played,
            },
            "monthly_stats": monthly_stats,
            "friends": [],
        }

        # Add some friends
        potential_friends = list(range(1, NUM_USERS + 1))
        potential_friends.remove(i)
        num_friends = random.randint(0, min(5, len(potential_friends)))
        friend_indices = random.sample(potential_friends, num_friends)

        users.append(user)

    for i, user in enumerate(users):
        potential_friends = list(range(NUM_USERS))
        potential_friends.remove(i)
        num_friends = random.randint(0, min(5, len(potential_friends)))
        friend_indices = random.sample(potential_friends, num_friends)

        user["friends"] = [
            str(users[friend_idx]["_id"]) for friend_idx in friend_indices
        ]

    # Create tables and games
    tables = []
    games = []

    for i in range(1, NUM_TABLES + 1):
        table_id = ObjectId()
        game_id = ObjectId()

        table_name = f"Table #{i} - {random.choice(['Friday Night', 'Weekend', 'Evening', 'Midday'])} Game"

        # Table details
        table_date = datetime.now(UTC) + timedelta(days=random.randint(1, 14))
        min_buy_in = random.choice([50, 100, 200, 500])
        max_players = random.randint(6, 10)
        game_type = "Texas Hold'em"
        blind_structure = random.choice(BLIND_STRUCTURES)
        venue = random.choice(VENUES)

        # Invite players
        creator_idx = random.randint(0, NUM_USERS - 1)
        creator_id = str(users[creator_idx]["_id"])

        num_players = random.randint(max(4, max_players - 2), max_players)
        player_indices = random.sample(range(NUM_USERS), num_players)

        players = []
        for player_idx in player_indices:
            status = random.choice(["invited", "confirmed", "declined"])
            if player_idx == creator_idx:
                status = "confirmed"

            players.append(
                {
                    "user_id": str(users[player_idx]["_id"]),
                    "username": users[player_idx]["username"],
                    "status": status,
                }
            )

        table = {
            "_id": table_id,
            "name": table_name,
            "date": table_date,
            "minimum_buy_in": min_buy_in,
            "maximum_players": max_players,
            "game_type": game_type,
            "blind_structure": blind_structure,
            "description": f"Regular {game_type} game with {blind_structure} blinds",
            "venue": venue,
            "creator_id": creator_id,
            "status": random.choice(
                ["scheduled", "in_progress", "completed", "cancelled"]
            ),
            "players": players,
            "created_at": datetime.now(UTC) - timedelta(days=random.randint(5, 30)),
            "updated_at": datetime.now(UTC) - timedelta(days=random.randint(0, 5)),
            "game_id": str(game_id),
        }

        tables.append(table)

        # Create game for this table
        game_date = datetime.now(UTC) - timedelta(days=random.randint(1, 90))
        confirmed_players = [p for p in players if p["status"] == "confirmed"]

        if len(confirmed_players) < 2:
            if len(players) >= 2:
                for i in range(min(2, len(players))):
                    players[i]["status"] = "confirmed"
                confirmed_players = [p for p in players if p["status"] == "confirmed"][
                    :2
                ]

        # Randomize actual attendees
        attending_players = random.sample(
            confirmed_players, random.randint(2, len(confirmed_players))
        )

        # Game status
        game_status = random.choice(
            ["completed", "completed", "completed", "in_progress"]
        )

        # Generate realistic financials
        total_pot = 0
        game_players = []

        for player in attending_players:
            # Buy-ins
            num_buy_ins = random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05])[0]
            buy_ins = []
            player_total_buy_in = 0

            for _ in range(num_buy_ins):
                amount = min_buy_in * random.randint(1, 2)
                buy_time = game_date + timedelta(minutes=random.randint(0, 180))
                buy_ins.append({"amount": amount, "time": buy_time})
                player_total_buy_in += amount
                total_pot += amount

            # Determine if player won or lost
            if game_status == "completed":
                win_factor = random.uniform(-0.5, 1.5)
                cash_out = int(player_total_buy_in * (1 + win_factor))
                net_profit = cash_out - player_total_buy_in
            else:
                # Game in progress - no cashout yet
                cash_out = 0
                net_profit = -player_total_buy_in

            # Notable hands
            notable_hands = []
            if random.random() < 0.3 and game_status == "completed":
                num_hands = random.randint(1, 3)
                for k in range(num_hands):
                    # Integer hand amounts
                    hand_amount = random.randint(
                        20, max(20, int(player_total_buy_in * 0.5))
                    )
                    hand_descriptions = [
                        f"Flopped a set of Aces against villain's top pair",
                        f"Rivered a straight against opponent's two pair",
                        f"Bluffed on the turn with a gutshot, opponent folded",
                        f"Slow-played Kings and got paid off by AQ",
                        f"Called down with second pair and was good",
                    ]
                    notable_hands.append(
                        {
                            "hand_id": f"hand_{game_id}_{k}",
                            "description": random.choice(hand_descriptions),
                            "amount_won": hand_amount,
                        }
                    )

            game_players.append(
                {
                    "user_id": player["user_id"],
                    "username": player["username"],
                    "buy_ins": buy_ins,
                    "cash_out": cash_out,
                    "net_profit": net_profit,
                    "notable_hands": notable_hands,
                }
            )

        if game_status == "completed" and game_players:
            total_net_profit = sum(player["net_profit"] for player in game_players)

            if total_net_profit != 0 and game_players:
                if total_net_profit > 0:
                    biggest_winner = max(game_players, key=lambda p: p["net_profit"])
                    idx = game_players.index(biggest_winner)
                    game_players[idx]["net_profit"] -= total_net_profit
                    game_players[idx]["cash_out"] = (
                        sum(b["amount"] for b in game_players[idx]["buy_ins"])
                        + game_players[idx]["net_profit"]
                    )
                else:
                    biggest_loser = min(game_players, key=lambda p: p["net_profit"])
                    idx = game_players.index(biggest_loser)
                    game_players[idx]["net_profit"] -= total_net_profit
                    game_players[idx]["cash_out"] = (
                        sum(b["amount"] for b in game_players[idx]["buy_ins"])
                        + game_players[idx]["net_profit"]
                    )

        # Game duration
        if game_status == "completed":
            duration_hours = random.randint(2, 8)
            duration_minutes = random.randint(0, 59)
        else:
            duration_hours = random.randint(0, 4)
            duration_minutes = random.randint(0, 59)

        game = {
            "_id": game_id,
            "table_id": str(table_id),
            "date": game_date,
            "venue": venue,
            "players": game_players,
            "status": game_status,
            "creator_id": creator_id,
            "duration": {"hours": duration_hours, "minutes": duration_minutes},
            "total_pot": total_pot,
            "created_at": game_date,
            "updated_at": game_date
            + timedelta(hours=duration_hours, minutes=duration_minutes),
        }

        games.append(game)

    # Print summary
    print(f"Generated:")
    print(f"- {len(users)} users")
    print(f"- {len(tables)} tables")
    print(f"- {len(games)} games")

    def insert_data_to_mongodb():
        from pymongo import MongoClient

        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/", tz_aware=True)
        db = client["PokerTracker"]

        # Delete existing data
        db.users.delete_many({})
        db.tables.delete_many({})
        db.games.delete_many({})

        print("Existing data deleted from MongoDB.")

        # Insert new data
        db.users.insert_many(users)
        db.tables.insert_many(tables)
        db.games.insert_many(games)

        print("New data inserted into MongoDB successfully!")

    insert_data_to_mongodb()


if __name__ == "__main__":
    main()
