from flask import Flask, render_template, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import random
from dotenv import load_dotenv, find_dotenv
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin

load_dotenv(find_dotenv())
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Person.query.get(int(user_id))

# returns a random movie from a list of some of my favorites
def getMovieInfo(movie_id):
    
    load_dotenv(find_dotenv())

    TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_MOVIE_SEARCH_PATH = "/movie/" + movie_id

    movie_response = requests.get(
        TMDB_API_BASE_URL + TMDB_MOVIE_SEARCH_PATH,
        params={
            "api_key": os.getenv("TMDB_API_KEY"),
        },
    )

    return movie_response.json()



# gets wikipedia link of a movie
def getWiki(movieName):

    WIKI_API_BASE_URL = "https://en.wikipedia.org/w/api.php"
    
    wiki_response = requests.get(
        WIKI_API_BASE_URL,
        params={
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": movieName
        },
    )
    if wiki_response.status_code == 200:
        movie_wiki_url = "https://en.wikipedia.org/?curid=" + \
                        str(wiki_response.json()["query"]["search"][0]["pageid"])
        return movie_wiki_url

    return None



# searches TMDB for an actor
def searchByActor(actorName):

    load_dotenv(find_dotenv())

    TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_MOVIE_SEARCH_PATH = "/search/person"

    search_response = requests.get(
        TMDB_API_BASE_URL + TMDB_MOVIE_SEARCH_PATH,
        params={
            "api_key": os.getenv("TMDB_API_KEY"),
            "query": actorName,
        },
    )


    if len(search_response.json()["results"]) == 0:
        return None

    length = len(search_response.json()["results"][0]["known_for"])
    random_movie_id = search_response.json()["results"][0]["known_for"][random.randint(0, length - 1)]["id"]
    return str(random_movie_id)



# searches TMDB for a movie
def searchByMovie(movieTitle):

    load_dotenv(find_dotenv())

    TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_MOVIE_SEARCH_PATH = "/search/movie"

    search_response = requests.get(
        TMDB_API_BASE_URL + TMDB_MOVIE_SEARCH_PATH,
        params={
            "api_key": os.getenv("TMDB_API_KEY"),
            "query": movieTitle,
        },
    )

    if len(search_response.json()["results"]) == 0:
        return None
    
    return str(search_response.json()["results"][0]["id"])



# creates a table of users
class Person(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"Person with username: {self.username}"

    def __init__(self, username):
        self.username = username


# creates a table of comments
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(100), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)
    movieTitle = db.Column(db.String(100), unique=False, nullable=False)
    
    def __repr__(self) -> str:
        return f"{self.username} commented {self.comment}"
    
    def __init__(self, username, comment, movieTitle):
        self.username = username
        self.comment = comment
        self.movieTitle = movieTitle


# create tables
with app.app_context():
    db.create_all()

# verifies if a user is valid or not
def validateUser(username):
    valid = db.session.query(Person.username).filter_by(username=username).scalar()
    return valid



# function to fetch comments
def getComments(movieTitle):
    comments = db.session.query(Comments).filter_by(movieTitle=movieTitle).limit(5).all()
    return comments



@app.route('/', methods=['GET', 'POST']) 
def index():

    list_of_movie_ids = ["157336", "78", "27205", "129", "169813"]

    # if the user does not enter anything
    if not request.args.get("input"):

        movie = getMovieInfo(random.choice(list_of_movie_ids))

    # if the user searches by movie title
    elif request.args.get("selection") == "movie":
        
        movie_id = searchByMovie(request.args.get("input"))

        if movie_id:
            movie = getMovieInfo(movie_id)
        else:
            flash("Unable to find a movie mathcing that title. Here's another great movie!")
            movie = getMovieInfo(random.choice(list_of_movie_ids))

        
    # if the user searches by actor
    elif request.args.get("selection") == "actor":
        
        movie_id = searchByActor(request.args.get("input"))

        if movie_id:
            movie = getMovieInfo(movie_id)
        else:
            flash("Unable to find any movies with that actor. Here's another random movie!")
            movie = getMovieInfo(random.choice(list_of_movie_ids))
  
    title = movie["title"]
    if movie["tagline"]:
        tagline = movie["tagline"]
    else:
        tagline = movie["overview"]
    genres = movie["genres"]
    if movie["poster_path"]:
        poster_url = "https://image.tmdb.org/t/p/original/" + movie["poster_path"]
    else:
        poster_url = None
    movie_wiki = getWiki(movie["title"])

    if request.method == "POST":
        if request.form["comment"]:
            if current_user.is_authenticated:
                movie = getMovieInfo(request.form['movie-id'])

                title = movie["title"]
                if movie["tagline"]:
                    tagline = movie["tagline"]
                else:
                    tagline = movie["overview"]
                genres = movie["genres"]
                if movie["poster_path"]:
                    poster_url = "https://image.tmdb.org/t/p/original/" + movie["poster_path"]
                else:
                    poster_url = None
                movie_wiki = getWiki(movie["title"])
            
                new_comment = Comments(current_user.username, request.form['comment'], title)
                db.session.add(new_comment)
                db.session.commit()
            else:
                flash("You must be logged in to comment.")

    movieID=movie['id']

    comments = getComments(movie['title'])

    return render_template('index.html',
                            title=title,
                            tagline=tagline,
                            genres=genres,
                            poster_url=poster_url,
                            movie_wiki=movie_wiki,
                            movieID=movieID,
                            comments=comments)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.args.get("username"):
        username = request.args.get("username")
        if validateUser(username):
            user = Person.query.filter_by(username=username).first()
            login_user(user) 
            return redirect(url_for('index'))
        else:
            flash(f"User with username: {username} not found")
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if not request.form['username']:
            flash("Please enter a unique username")
        else:
            username = request.form['username']
            if not validateUser(username):
                user = Person(username)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("That username is already in use. Please enter a new one.")
    return render_template("signup.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    app.secret_key = os.getenv("SECRET_KEY")
    app.config["SESSION_TYPE"] = "filesystem"
    # app.run()

