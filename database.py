"""Database to hold card game info"""
import sqlite3
from deck_blackjack import Card

class GamesDatabase:
    """Class for a games database"""
    def __init__(self):
        self.connection = sqlite3.connect("test_db.db")
        self.createGamesTable()

    def createGamesTable(self):
        """Creates the games table in the games database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS games(
                    status,
                    num_games,
                    player,
                    suit,
                    face_value,
                    card_value,
                    PRIMARY KEY (num_games, player, suit, face_value)
                )
                """
            )

            # self.addCard(Card("♦", "Diamonds", "6", "6"), 1, "Player 1")

            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()

    def gameNum(self, game_num):
        """Set current game number based on previous maximum num_games,
        unless a non-zero game number is passed in"""
        curs = self.connection.cursor()
        if game_num == 0:
            curs.execute(
                """
                SELECT MAX(num_games)
                FROM games
                """
            )
            result = curs.fetchone()
            if result[0] is not None:
                # Fetch returns a tuple, so access by index
                return result[0] + 1
            return 1
        else:
            return game_num

    def addCard(self, status: str, num_games: int, player: str, card: Card):
        """Add a card and player to the database"""
        try:
            curs = self.connection.cursor()
            # Use cursor to insert records into games table.
            curs.execute(
                f"""
                INSERT INTO games (
                    status,
                    num_games,
                    player,
                    suit,
                    face_value,
                    card_value
                ) VALUES (
                    '{status}',
                    {num_games},
                    '{player}',
                    '{card.suit_name}',
                    '{card.value}',
                    {card.card_value}
                )
                ON CONFLICT (num_games, player, suit, face_value)
                DO UPDATE
                SET
                    status = excluded.status,
                    card_value = excluded.card_value
                """
            )
            self.connection.commit()
        except Exception as e2:
            print(e2)
        # print(self.printGames())

    def clearGamesTable(self):
        """Clears games table"""
        # If there is something in the table, clear it
        if self.printGames():
            try:
                curs = self.connection.cursor()
                curs.execute("DELETE FROM games")
                self.connection.commit()
            except Exception as e2:
                print(e2)
                self.connection.rollback()

    def printGames(self):
        """Gets entries from database"""
        curs = self.connection.cursor()
        all_games = curs.execute(
            """
            SELECT status, num_games, player, suit, face_value, card_value FROM games
            """
        )
        return all_games.fetchall()

    def selectGame(self, game_num: int):
        """Gets all entries for specified game number"""
        curs = self.connection.cursor()
        selected_entries = curs.execute(
            f"""
            SELECT status, num_games, player, suit, face_value, card_value FROM games
            WHERE num_games={game_num}
            """
        )
        game_contents = [{
            "status": entry[0],
            "num_games": entry[1],
            "player": entry[2],
            "suit": entry[3],
            "face_value": entry[4],
            "card_value": entry[5],
        } for entry in selected_entries.fetchall()]
        return game_contents

    def selectGameStatus(self, status: str):
        """Gets num_games where game is paused or gets win/loss/tie records"""
        curs = self.connection.cursor()
        if status == "p":
            selected_games = curs.execute(
                """
                SELECT DISTINCT num_games FROM games
                WHERE status=?
                """, (status)
            )
            result = [res[0] for res in selected_games.fetchall()]
        else:
            won_games = curs.execute(
                """
                SELECT DISTINCT num_games FROM games
                WHERE status='w'
                """
            )
            won = len([res[0] for res in won_games.fetchall()])
            lost_games = curs.execute(
                """
                SELECT DISTINCT num_games FROM games
                WHERE status='l'
                """
            )
            lost = len([res[0] for res in lost_games.fetchall()])
            tie_games = curs.execute(
                """
                SELECT DISTINCT num_games FROM games
                WHERE status='t'
                """
            )
            tie = len([res[0] for res in lost_games.fetchall()])
            result = [won, lost, tie]
        # Unpack list of tuples, return as list of ints
        return result        

games_db = GamesDatabase()
# games_db.selectGame(2)
