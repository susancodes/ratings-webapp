"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app
import datetime

def load_users():
    """Load users from u.user into database."""
    the_file = open("./seed_data/u.user")
    for line in the_file:
        split_line = line.rstrip().split("|")
        user_id = split_line[0]
        age = split_line[1]
        zipcode = split_line[4]
        new_user = User(user_id=user_id, age=age, zipcode=zipcode)
        db.session.add(new_user)
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""
    the_file = open("./seed_data/u.item")
    for line in the_file:
        split_line = line.rstrip().split("|")
        movie_id = split_line[0]
        title = split_line[1]
        def remove_parentheses(s): 
            result = "" 
            flag = True 
            for c in s: 
                if c == "(": flag = False 
                if flag: result += c 
                if c == ")": flag = True 
            return result
        title = remove_parentheses(title)
        released_at = split_line[2]
        if released_at == '':
            released_at = None
        else:
            released_at = datetime.datetime.strptime(released_at, "%d-%b-%Y")
        print movie_id, title, released_at
        imdb_url = split_line[4]
        new_movie = Movie(movie_id=movie_id, title=title, released_at=released_at, imdb_url=imdb_url)
        db.session.add(new_movie)
    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""
    the_file = open("./seed_data/u.data")
    for line in the_file:
        split_line = line.rstrip().split("\t")
        user_id = split_line[0]
        movie_id = split_line[1]
        score = split_line[2]
        new_rating = Rating(user_id=user_id, movie_id=movie_id, score=score)
        db.session.add(new_rating)
    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_movies()
    load_ratings()
