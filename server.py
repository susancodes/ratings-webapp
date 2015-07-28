"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

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

    if email:
        session["email"] = email
        flash("You are now logged in.")
    return redirect('/')

@app.route('/logout', methods=["POST"])
def handle_logout():
    """Process user logout."""

    session["email"] = ""
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
    users_movies = Rating.query.filter_by(user_id=id).all()
    movie_dict = {}
    for movie in users_movies:
        movie_id = movie.movie_id
        movie_object = Movie.query.get(movie_id)
        movie_dict[movie_object] = movie.score
    return render_template('about_user.html', 
                            id=id,
                            age=user.age,
                            zipcode=user.zipcode,
                            movie_dict=movie_dict)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()