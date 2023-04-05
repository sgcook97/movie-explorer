from flask import Flask, render_template, request, flash
import json
import os
import requests
import random
from dotenv import load_dotenv, find_dotenv

app = Flask(__name__)

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



@app.route('/') 
def main():

    list_of_movie_ids = ["157336", "78", "27205", "129", "169813"]

    # if the user does not enter anything
    if not request.args.get("input"):

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

        return render_template('index.html',
                                   title=title,
                                   tagline=tagline,
                                   genres=genres,
                                   poster_url=poster_url,
                                   movie_wiki=movie_wiki)

    # if the user searches by movie title
    if request.args.get("selection") == "movie":
        
        movie_id = searchByMovie(request.args.get("input"))

        if movie_id:
            movie = getMovieInfo(movie_id)
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
            return render_template("index.html",
                                   title=title,
                                   tagline=tagline,
                                   genres=genres,
                                   poster_url=poster_url,
                                   movie_wiki=movie_wiki)
        else:
            flash("Unable to find a movie mathcing that title. Here's another great movie!")
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
            return render_template("index.html",
                                   title=title,
                                   tagline=tagline,
                                   genres=genres,
                                   poster_url=poster_url,
                                   movie_wiki=movie_wiki)
        
    # if the user searches by actor
    if request.args.get("selection") == "actor":
        
        movie_id = searchByActor(request.args.get("input"))

        if movie_id:
            movie = getMovieInfo(movie_id)
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
            return render_template("index.html",
                                   title=title,
                                   tagline=tagline,
                                   genres=genres,
                                   poster_url=poster_url,
                                   movie_wiki=movie_wiki)
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
            return render_template("index.html",
                                   title=title,
                                   tagline=tagline,
                                   genres=genres,
                                   poster_url=poster_url,
                                   movie_wiki=movie_wiki)

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    app.secret_key = os.getenv("SECRET_KEY")
    app.config["SESSION_TYPE"] = "filesystem"
    #app.run()