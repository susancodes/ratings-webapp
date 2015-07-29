"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from sortedcontainers import SortedDict
from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route('/login_form')
def login():
    """Login."""

    return render_template("login.html")

@app.route('/login_handler', methods=["POST"])
def handle_login():
    """Process login info."""

    email = request.form.get("email")
    password = request.form.get("password")

    #If both email and password are correct, log them in
    if User.query.filter(User.email == email, User.password == password).first():
        flash("You are now logged in.")
        session["email"] = email
    #if email is correct but not password, tell them they fucked up
    elif User.query.filter(User.email == email, User.password != password).first(): 
        flash("Incorrect login information provided. Please try again.")
        return redirect("/login_form")
    #If both email and pass were incorrect, make a new user
    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Welcome new user. You've been added to our database!")
        session["email"] = email
    return redirect('/')


@app.route('/logout', methods=["POST"])
def handle_logout():
    """Process user logout."""

    del session["email"]
    flash("You are now logged out.")
    return redirect('/')

@app.route("/users")
def user_list():
    """Show list of user."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/users/<int:id>")
def show_user_info(id):
    """Show user info."""

    user = User.query.get(id)
    users_ratings = user.ratings

    movie_dict = {}
    for rating in users_ratings:
        movie_dict[rating.movie] = rating.score
        print rating

    return render_template('about_user.html', 
                            id=id,
                            age=user.age,
                            zipcode=user.zipcode,
                            ratings=users_ratings,
                            movie_dict=movie_dict)

@app.route("/add_rating", methods=["POST"])
def add_rating():
    user_email = session["email"]
    user = User.query.filter_by(email=user_email).first()
    movie_id = request.form.get("movie_id")
    score = request.form.get("score")
    # If this user has rated this film with the same score, do nothing
    if Rating.query.filter(Rating.user_id == user.user_id, 
                            Rating.movie_id == movie_id,
                            Rating.score == score).first():
        pass

    # If this user has rated this film with a different score, update the score
    elif Rating.query.filter(Rating.user_id == user.user_id, 
                            Rating.movie_id == movie_id,
                            Rating.score != score).first():
        old_rating = Rating.query.filter(Rating.user_id == user.user_id, 
                            Rating.movie_id == movie_id).first()
        old_rating.score = score
        db.session.commit()

    # If this user has never rated this movie, add a rating for it
    else:
        new_user_rating = Rating(user_id=user.user_id, movie_id=movie_id, score=score)
        db.session.add(new_user_rating)
        db.session.commit()
    
    return render_template('rating_test.html',
                            user_id=user.user_id,
                            movie_id=movie_id,
                            score=score)

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)

@app.route("/movies/<int:id>")
def show_movie_info(id):
    """Show movie info."""

    movie_object = Movie.query.get(id)
    movies_ratings = movie_object.ratings

    movie_dict = {}
    for movie in movies_ratings:
        movie_dict[movie.user] = movie.score

    # ratings_list = db.session.query(User.user_id, Rating.score).join(Rating).all()

    return render_template('about_movie.html', 
                            movie_object=movie_object,
                            movie_dict=movie_dict)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()