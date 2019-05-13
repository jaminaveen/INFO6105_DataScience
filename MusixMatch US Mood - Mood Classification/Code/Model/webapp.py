from flask import Flask, render_template, request, url_for,flash,redirect,session
from get_lyrics_and_moods import *
import os
import pickle

application = app = Flask(__name__)



@app.route("/home")
@app.route("/", methods=["GET", "POST"])
def home():
    error = "None"
    try:
        if request.method == "POST":
            session["user_name"] = request.form["user_name"]
            session["song_nos"] = request.form["song_nos"]
            song_nos = request.form["song_nos"]
            # my_song_df = dummy_main(song_nos)
            # data = my_song_df.to_dict(orient="records")
            return redirect(url_for("index"))
        else:
            return render_template('home.html')
    except Exception as e:
        error = "Provide valid input"
        return render_template('home.html')

@app.route("/index", methods=["GET", "POST"])
def index():
    error = "None"
    try:
        if request.method == "POST":
            song_name = request.form["song_name"]
            artist_name = request.form["artist_name"]
            lyrics = get_lyrics_by_api_call(song_name, artist_name)
            lyrics_dict = lyrics.to_dict(orient="records")
            headers = lyrics.columns
            # with open('filename.pickle', 'rb') as handle:
            #     df = pickle.load(handle)
            my_song_df = dummy_main(session["song_nos"])
            data = my_song_df.to_dict(orient="records")
            return render_template("index.html", data=data, lyrics_dict=lyrics_dict,error=error, headers=headers, user_name = session["user_name"])
        if request.method == "GET":
            my_song_df = dummy_main(session["song_nos"])
            data = my_song_df.to_dict(orient="records")
            headers = my_song_df.columns
            return render_template("index.html", data=data, error=error, headers=headers, user_name = session["user_name"])

    except Exception as e:
        error = "Please provide correct Song and Artist Name "
        with open('filename.pickle', 'rb') as handle:
            df = pickle.load(handle)
        data = df.to_dict(orient="records")
        headers = df.columns
        return render_template("index.html", data=data, error=error, headers=headers, user_name = session["user_name"])

@app.route("/mood")
# @app.route("/")
def mood():
    with open('filename.pickle', 'rb') as handle:
        data = pickle.load(handle)
    word_cloud(data)
    ### Rendering Plot in Html
    image_names =[]
    image_names.append("happy.png")
    image_names.append("/sad.png")
    print(image_names)
    return render_template("about.html", image_names=image_names)
    #return render_template('home.html')


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)