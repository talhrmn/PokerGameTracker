import random
from datetime import datetime, timedelta, UTC

from bson import ObjectId
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


# Generate test data
NUM_USERS = 10
NUM_TABLES = 20
PASSWORD = "123!@#qweQWE"
PASSWORD_HASH = get_password_hash(PASSWORD)
VENUES = ["Home Game", "Casino Royale", "The Poker Room", "Underground", "VIP Lounge"]
BLIND_STRUCTURES = ["1/2", "2/5", "5/10", "10/20", "25/50"]


def get_recent_months():
    """Generate list of recent months including current month"""
    current_date = datetime.now(UTC)
    months = []

    for i in range(6):  # Last 6 months including current
        month_date = current_date - timedelta(days=30 * i)
        month_str = month_date.strftime("%b %Y")
        months.append(month_str)

    return list(reversed(months))  # Oldest to newest


def main():
    # Create users
    users = []
    for i in range(1, NUM_USERS + 1):
        user_id = ObjectId()
        username = f"user_{i}"
        email = f"user_{i}@gmail.com"

        user = {
            "_id": user_id,
            "username": username,
            "email": email,
            "password_hash": PASSWORD_HASH,
            "profile_pic": None,
            "created_at": datetime.now(UTC) - timedelta(days=random.randint(1, 365)),
            "last_login": datetime.now(UTC) - timedelta(days=random.randint(0, 30)),
            "friends": []
        }

        users.append(user)

    # Initialize empty friends lists (will be populated after games are created)
    for user in users:
        user["friends"] = []

    # Create tables and games with proper synchronization
    tables = []
    games = []

    for i in range(1, NUM_TABLES + 1):
        table_id = ObjectId()
        game_id = ObjectId()

        table_name = f"Table #{i} - {random.choice(['Friday Night', 'Weekend', 'Evening', 'Midday'])} Game"

        # Determine table status first - this drives everything else
        table_status = random.choice(["scheduled", "in_progress", "completed", "cancelled"])

        # Set dates based on status
        if table_status == "scheduled":
            table_date = datetime.now(UTC) + timedelta(days=random.randint(1, 14))
            game_date = None  # No game yet for scheduled tables
        elif table_status == "in_progress":
            table_date = datetime.now(UTC) - timedelta(hours=random.randint(1, 8))
            game_date = table_date
        elif table_status == "completed":
            table_date = datetime.now(UTC) - timedelta(days=random.randint(1, 30))
            game_date = table_date
        else:  # cancelled
            table_date = datetime.now(UTC) - timedelta(days=random.randint(1, 14))
            game_date = None  # No game for cancelled tables

        # Table details
        min_buy_in = random.choice([50, 100, 200, 500])
        max_players = random.randint(6, 10)
        game_type = "Texas Hold'em"
        blind_structure = random.choice(BLIND_STRUCTURES)
        venue = random.choice(VENUES)

        # Create players
        creator_idx = random.randint(0, NUM_USERS - 1)
        creator_id = str(users[creator_idx]["_id"])

        num_invited = random.randint(max_players - 2, max_players + 2)
        player_indices = random.sample(range(NUM_USERS), min(num_invited, NUM_USERS))

        players = []
        for player_idx in player_indices:
            if player_idx == creator_idx:
                status = "confirmed"  # Creator is always confirmed
            elif table_status == "cancelled":
                status = random.choice(["invited", "confirmed", "declined"])
            else:
                # For active/completed tables, ensure we have enough confirmed players
                status = random.choices(
                    ["confirmed", "declined", "invited"],
                    weights=[0.7, 0.2, 0.1]
                )[0]

            players.append({
                "user_id": str(users[player_idx]["_id"]),
                "username": users[player_idx]["username"],
                "status": status
            })

        # Ensure we have at least 2 confirmed players for non-cancelled tables
        if table_status != "cancelled":
            confirmed_count = sum(1 for p in players if p["status"] == "confirmed")
            if confirmed_count < 2:
                # Convert some declined/invited to confirmed
                non_confirmed = [p for p in players if p["status"] != "confirmed"]
                needed = min(2 - confirmed_count, len(non_confirmed))
                for i in range(needed):
                    non_confirmed[i]["status"] = "confirmed"

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
            "status": table_status,
            "players": players,
            "created_at": datetime.now(UTC) - timedelta(days=random.randint(5, 30)),
            "updated_at": datetime.now(UTC) - timedelta(days=random.randint(0, 5)),
            "game_id": str(game_id)
        }

        tables.append(table)

        # Create game only if table is not scheduled or cancelled
        if game_date is not None:
            confirmed_players = [p for p in players if p["status"] == "confirmed"]

            # Determine who actually showed up (90% chance for confirmed players)
            attending_players = []
            for player in confirmed_players:
                if random.random() < 0.9:  # 90% show rate
                    attending_players.append(player)

            # Ensure at least 2 players if we're creating a game
            if len(attending_players) < 2 and len(confirmed_players) >= 2:
                attending_players = confirmed_players[:2]

            # Set game status based on table status
            if table_status == "completed":
                game_status = "completed"
            elif table_status == "in_progress":
                game_status = "in_progress"
            else:
                game_status = "completed"  # Fallback

            # Generate realistic financials with proper balancing
            game_players = []
            total_buy_ins = 0

            for player in attending_players:
                # Generate buy-ins
                num_buy_ins = random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05])[0]
                buy_ins = []
                player_total_buy_in = 0

                for j in range(num_buy_ins):
                    amount = min_buy_in * random.choice([1, 1.5, 2])
                    buy_time = game_date + timedelta(minutes=random.randint(0, 180))
                    buy_ins.append({
                        "amount": int(amount),
                        "time": buy_time
                    })
                    player_total_buy_in += int(amount)

                total_buy_ins += player_total_buy_in

                # Initialize with buy-in amount (will be adjusted later)
                game_players.append({
                    "user_id": player["user_id"],
                    "username": player["username"],
                    "buy_ins": buy_ins,
                    "cash_out": 0,  # Will be set below
                    "net_profit": 0,  # Will be calculated below
                    "notable_hands": []
                })

            # Distribute the money realistically for completed games
            if game_status == "completed" and game_players:
                # Generate random cash-outs that sum to total buy-ins
                remaining_pot = total_buy_ins

                for i, player in enumerate(game_players):
                    player_buy_in = sum(b["amount"] for b in player["buy_ins"])

                    if i == len(game_players) - 1:
                        # Last player gets whatever is left
                        cash_out = remaining_pot
                    else:
                        # Random distribution with some bias toward not losing everything
                        min_cashout = max(0, int(player_buy_in * 0.1))  # Lose at most 90%
                        max_cashout = min(remaining_pot, int(total_buy_ins * 0.4))  # Win at most 40% of total pot

                        if max_cashout > min_cashout:
                            cash_out = random.randint(min_cashout, max_cashout)
                        else:
                            cash_out = min_cashout

                    player["cash_out"] = cash_out
                    player["net_profit"] = cash_out - player_buy_in
                    remaining_pot -= cash_out

                # Generate notable hands for winners
                for player in game_players:
                    if player["net_profit"] > 20 and random.random() < 0.4:  # Only for players who won more than $20
                        num_hands = random.randint(1, 2)
                        for k in range(num_hands):
                            # Ensure valid range for hand amount
                            max_hand_amount = min(100, abs(player["net_profit"]))
                            min_hand_amount = min(20, max_hand_amount)

                            if max_hand_amount >= min_hand_amount:
                                hand_amount = random.randint(min_hand_amount, max_hand_amount)
                            else:
                                hand_amount = max_hand_amount

                            hand_descriptions = [
                                f"Flopped a set of Aces against villain's top pair",
                                f"Rivered a straight against opponent's two pair",
                                f"Bluffed on the turn with a gutshot, opponent folded",
                                f"Slow-played Kings and got paid off by AQ",
                                f"Called down with second pair and was good"
                            ]
                            player["notable_hands"].append({
                                "hand_id": f"hand_{game_id}_{player['user_id']}_{k}",
                                "description": random.choice(hand_descriptions),
                                "amount_won": hand_amount
                            })

            else:
                # Game in progress - no cash-outs yet
                for player in game_players:
                    player_buy_in = sum(b["amount"] for b in player["buy_ins"])
                    player["cash_out"] = 0
                    player["net_profit"] = -player_buy_in  # Currently losing buy-in

            # Game duration
            if game_status == "completed":
                duration_hours = random.randint(2, 8)
                duration_minutes = random.randint(0, 59)
                updated_at = game_date + timedelta(hours=duration_hours, minutes=duration_minutes)
            else:
                # In progress
                elapsed_hours = random.randint(1, 4)
                elapsed_minutes = random.randint(0, 59)
                duration_hours = elapsed_hours
                duration_minutes = elapsed_minutes
                updated_at = game_date + timedelta(hours=elapsed_hours, minutes=elapsed_minutes)

            game = {
                "_id": game_id,
                "table_id": str(table_id),
                "date": game_date,
                "venue": venue,
                "players": game_players,
                "status": game_status,
                "creator_id": creator_id,
                "duration": {
                    "hours": duration_hours,
                    "minutes": duration_minutes
                },
                "total_pot": total_buy_ins,
                "created_at": game_date,
                "updated_at": updated_at
            }

            games.append(game)

    # Create friendships based on who played together
    print("Creating friendships based on game participation...")

    # Create a mapping from user_id to user index for quick lookup
    user_id_to_index = {str(user["_id"]): i for i, user in enumerate(users)}

    # Track all connections made through games
    for game in games:
        player_user_ids = [p["user_id"] for p in game["players"]]

        # Make all players in this game friends with each other
        for i, user_id_1 in enumerate(player_user_ids):
            for j, user_id_2 in enumerate(player_user_ids):
                if i != j:  # Don't add self as friend
                    user_idx_1 = user_id_to_index[user_id_1]

                    # Add user_id_2 to user_1's friends list if not already there
                    if user_id_2 not in users[user_idx_1]["friends"]:
                        users[user_idx_1]["friends"].append(user_id_2)

    # Also add some random additional friendships to make it more realistic
    # (people can be friends without having played together yet)
    for i, user in enumerate(users):
        current_friends = set(user["friends"])
        potential_friends = [str(users[j]["_id"]) for j in range(NUM_USERS) if j != i]
        available_friends = [f for f in potential_friends if f not in current_friends]

        # Add 0-3 additional random friends
        if available_friends:
            num_additional = random.randint(0, min(3, len(available_friends)))
            additional_friends = random.sample(available_friends, num_additional)
            user["friends"].extend(additional_friends)

            # Make friendships mutual
            for friend_id in additional_friends:
                friend_idx = user_id_to_index[friend_id]
                if str(user["_id"]) not in users[friend_idx]["friends"]:
                    users[friend_idx]["friends"].append(str(user["_id"]))

    # Create separate statistics records for each user
    statistics = []
    recent_months = get_recent_months()

    for user in users:
        # Generate monthly stats for recent months including current month
        monthly_stats = []
        for month in recent_months:
            # Generate realistic monthly data
            monthly_games_won = random.randint(0, 4)
            monthly_games_lost = random.randint(0, 4)
            monthly_tables = monthly_games_won + monthly_games_lost

            # Generate profit based on win/loss ratio
            if monthly_games_won > monthly_games_lost:
                monthly_profit = random.randint(50, 500)
            elif monthly_games_won < monthly_games_lost:
                monthly_profit = random.randint(-400, -20)
            else:
                monthly_profit = random.randint(-100, 100)

            monthly_hours = monthly_tables * random.uniform(3, 6) if monthly_tables > 0 else 0

            monthly_stats.append({
                "month": month,
                "profit": monthly_profit,
                "games_won": monthly_games_won,
                "games_lost": monthly_games_lost,
                "tables_played": monthly_tables,
                "hours_played": round(monthly_hours, 1)
            })

        # Calculate main stats as sum of all monthly stats
        total_profit = sum(month["profit"] for month in monthly_stats)
        total_games_won = sum(month["games_won"] for month in monthly_stats)
        total_games_lost = sum(month["games_lost"] for month in monthly_stats)
        total_tables_played = sum(month["tables_played"] for month in monthly_stats)
        total_hours_played = sum(month["hours_played"] for month in monthly_stats)

        # Create statistics record with updated schema
        stat_record = {
            "_id": ObjectId(),
            "user_id": user["_id"],
            "updated_at": datetime.now(UTC),
            "stats": {
                "total_profit": total_profit,
                "games_won": total_games_won,
                "games_lost": total_games_lost,
                "tables_played": total_tables_played,
                "hours_played": round(total_hours_played, 1)
            },
            "monthly_stats": monthly_stats
        }

        statistics.append(stat_record)

    # Print summary
    print(f"\nGenerated:")
    print(f"- {len(users)} users")
    print(f"- {len(statistics)} statistics records")
    print(f"- {len(tables)} tables")
    print(f"- {len(games)} games")

    # Print friendship statistics
    total_friendships = sum(len(user["friends"]) for user in users)
    avg_friends = total_friendships / len(users) if users else 0
    print(f"- {total_friendships} total friendship connections")
    print(f"- Average {avg_friends:.1f} friends per user")

    # Print status breakdown
    table_statuses = {}
    game_statuses = {}

    for table in tables:
        status = table["status"]
        table_statuses[status] = table_statuses.get(status, 0) + 1

    for game in games:
        status = game["status"]
        game_statuses[status] = game_statuses.get(status, 0) + 1

    print(f"\nTable statuses: {table_statuses}")
    print(f"Game statuses: {game_statuses}")
    print(f"\nMonthly data includes: {', '.join(recent_months)}")

    # Verify financial consistency for completed games
    print(f"\nFinancial verification:")
    for game in games:
        if game["status"] == "completed":
            total_buy_ins = sum(sum(b["amount"] for b in p["buy_ins"]) for p in game["players"])
            total_cash_outs = sum(p["cash_out"] for p in game["players"])
            print(
                f"Game {game['_id']}: Buy-ins=${total_buy_ins}, Cash-outs=${total_cash_outs}, Balanced: {total_buy_ins == total_cash_outs}")

    def insert_data_to_mongodb():
        from pymongo import MongoClient

        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/", tz_aware=True)
        db = client["PokerTracker"]

        # Delete existing data
        db.users.delete_many({})
        db.statistics.delete_many({})
        db.tables.delete_many({})
        db.games.delete_many({})

        print("\nExisting data deleted from MongoDB.")

        # Insert new data
        db.users.insert_many(users)
        db.statistics.insert_many(statistics)
        db.tables.insert_many(tables)
        db.games.insert_many(games)

        print("New data inserted into MongoDB successfully!")

    insert_data_to_mongodb()


if __name__ == "__main__":
    main()
