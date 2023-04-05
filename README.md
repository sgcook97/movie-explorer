# Movie Explorer

This web app can be reached at https://movie-explorer.fly.dev 

This project is a web app using flask and fly.io that allows the user to either see information from one of a few of my favorite movies, search for a movie by title, or search an actors name which will cause a random movie with that actor to be displayed. This information is retrieved using  TMDB API and the MediaWiki API.


## Setup
To run this on your own device, first clone the repo.

You need to install the necessary requirements for the app to run. you can do this by running the following command in your terminal.

    python -m pip install -r requirements.txt

Before continuing, you will need to get an API key from TMDB. 
* First, create an account at https://www.themoviedb.org
* Next, go to your profile settings and on the left hand side, navigate to the section labeled API
* Follow the steps there to apply for the key and you're good to go

Now that you have your key, we need to store it as an environment variable to keep it secure.

Create a .env file and save the key as a variable named TMDB_API_KEY.
At this point you should also create a variable named SECRET_KEY and assign it a random secret key. This is neccessary for the app to run with flask.

Once this is done, just uncomment out the last line of code in movie-explorer.py that says app.run(), and run the code.

The app should now be running and available through the link that pops up in the terminal.


## Challenges
* Many times I was not indexing properly when accessing the json objects returned by the API. To fix these issues, I re-read the API documentation carefuly a few times over and tested until it was working.

* I had trouble dealing with getting unexpected responses from the API. I then realized that many of my problems were coming from returning a json object even when it was an error response. I fixed this by checking the response type before returning it, and then returning a null value if it was incorrect.

* When deploying, my app initially would fail over and over again. After much time researching why, it boiled down to being due to the fact that gunicorn was not being installed on the virtual machine. It was not included in the requirements.txt for some reason, so I just manually wrote it in and it worked.


### Ongoing Problems

* One issue that is not fixed yet is that the container that the movie is stored in will grow past the height of the contents inside of it. This is probably a simple fix, but I chose to move on and focus on finishing the rest of the project.

* Another issue that is still ongoing is that the wiki links found throught the API are not always correct. This could be fixed by adding more search parameters, but it is difficult to find the right ones.