"""Models and database functions for Ratings project."""
import correlation
from flask_sqlalchemy import SQLAlchemy

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

# Delete this line and put your User/Movie/Ratings model classes here.
class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)

class Movie(db.Model):
    """Movies of ratings website."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Movie movie_id=%s title=%s>" % (self.movie_id, self.title)

class Rating(db.Model):
    """Ratings of ratings website."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

     # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("ratings", order_by=rating_id))

    # Define relationship to movie
    movie = db.relationship("Movie",
                            backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Rating rating_id=%s movie_id=%s user_id=%s score=%s>" % (
            self.rating_id, self.movie_id, self.user_id, self.score)

##############################################################################
# Algorithm Stuff

def find_common_users(movie_id):
    """Gets a list of all the ratings a movie has,
    then turns the list of ratings into a list 
    of the users who authored them."""

    ratings_list = Rating.query.filter(Rating.movie_id==movie_id).all()
    users = []
    for rating in ratings_list:
        user = rating.user
        users.append(user)

    we_are = User.query.get(944)
    our_ratings = we_are.ratings

    u_ratings = {}
    for rating in our_ratings:
        u_ratings[rating.movie_id] = rating

    # CONFIRMED WORKING UP UNTIL THIS POINT

    paired_ratings = []
    for rating in ratings_list:
        our_rating = u_ratings.get(rating.movie_id)
        if our_rating is not None:
            pair = (our_rating.score, rating.score)
            paired_ratings.append(pair)

    print paired_ratings

def similarity(user1, user2):
    """Return pearson rating for user1 compared to user2."""

    u_ratings = {}
    paired_ratings = []

    for r in user1.ratings:
        u_ratings[r.movie_id] = r

    for r in user2.ratings:
        u_r = u_ratings.get(r.movie_id)
        if u_r is not None:
            paired_ratings.append( (u_r.score, r.score) )

    if paired_ratings:
        return correlation.pearson(paired_ratings)

    else:
        return 0.0


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."