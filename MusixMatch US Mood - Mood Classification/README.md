
# Song_Mood_Classifier_Flask_Web_App <br>
Machine learning model to classify mood of the song as Happy/Sad <br>

# Goal: <br>
- Mood classifier for a top-k list <br>
- Displaying mood of the song using Search <br>

# To use the model 
Download the model using song_mood_mlp_model.h5 from Model folder <br>
new_model = keras.models.load_model('song_mood_mlp_model.h5') <br>

## we have created an Application using : FLASK and HEROKU <br>
The WEB App would provide the user with 2 functionalities: <br>
1. Displaying the user with the list of top songs across the globe with the mood of the songs as Happy or Sad <br>
2. Allowing the user to search the song mood by searching the song name and artist name <br>
3. URL for the APP : https://musicmoodapp.herokuapp.com/ <br>

<b> APP SCREENSHOT </b>
![Capture](https://user-images.githubusercontent.com/37238004/55662335-341b3580-57e0-11e9-8a41-d2a723c7c4d0.JPG)

# CLAAT
<b> https://codelabs-preview.appspot.com/?file_id=1mmqN8t1Q9ZbYELVA_Tud2Eo3u9vxU_OXMjDYfbq-RJ0#0 </b>

# YOUTUBE 
<b> https://youtu.be/9trHX5Ahjx8 </b>

# References:
- https://github.com/rasbt/musicmood
- https://developers.google.com/machine-learning/guides/text-classification/
- https://developer.musixmatch.com
- https://github.com/google/eng-edu/tree/master/ml/guides/text_classification
