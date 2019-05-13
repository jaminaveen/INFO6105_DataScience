## Graduate Admission Predictor for student and University
Today, there are many students who travel to USA to pursue higher education. It is necessary for the students to know what are their chances of getting an admit in the universities. <br>
Also, universities manually check and count the total number of applicants who could get an admit into university. These methods are slow and certainly not very consistent for students and universities to get an actual result. This method is also prone to human error and thus accounts for some inaccuracies. Since the frequency of students studying abroad has increased, there is a need to employ more efficient systems which handle the admission process accurately from both perspectives<br><br>

<b><u>GOAL</u></b><br>
The goal of the model is to cover two aspects of Graduate Admission:<br>
 - Students : Building a Machine Learning model to help the aspiring graduate students to narrow down the universities choices in Computer Science in USA<br>
 - University: Building a Machine Learning model to assist the university in selecting suitable candidates for the CS Program<br><br>

<b> <u>APPROACH</u> </b><br>
- Data Gathering : Scraped the dataset from Yocket, Edulix which consists of 9 columns and 9351 for 29 universities in USA<br>
- Data cleaning, Data Processing feature Engineering<br>
- Data Models for students and University : Classification Models<br>
- Error metrices calculation: Using confusion metrix to calculate Accuracy,F1 score and AUC curve<br>
- Pipeling: Using Dask for Pipelining<br>
- Dockerizing: Dockerizing the environment<br>
- Deployment: deploying the code on Heroku and Amazon AWS S3<br><br>

<b> <u>DATASET</u></b><br>
 - Assisting Student Model : Dataset for 29 colleges across USA ranging from Rank 1 to Rank 130 in computer science department<br>
 - Assidting University Model: Dataset for Northeastern University, Boston<br><br><br>

<b><u>USING THE APPLICATION</b></u><br>
#### Assisting Student Model :<br>
<b>URL for the application:</b> https://grad-school-predictor.herokuapp.com/ <br>
Steps to reproduce:<br> 
- Covers 2 functionality of showing acceptance.rejection of the college<br>
- Also displaying him with the list of 5 colleges where they will be likely to get most admits
![image](https://user-images.githubusercontent.com/37238004/56715198-ff2a4080-6704-11e9-9e65-6cef85daefbb.png)

##### Assisting University Model :<br>
Steps to reproduce:<br> This is for the Northeastern University to admit or reject a candidate based on the model prediction
![image](https://user-images.githubusercontent.com/37238004/56716147-92fd0c00-6707-11e9-8e26-caaa72edd874.png)
<br>
<br>
<b> TO RUN DOCKER IMAGE <b>
 - Pull docker image for webApp --> docker pull naveenjami/gradadmissionpredictor<br>
 - Run on docker  --> docker run -p laptopport:5000 naveenjami/gradadmissionpredictor
 - Run on browser --> http://dockerIP:laptopport <br>
![image](https://user-images.githubusercontent.com/37238004/56794222-ada0b500-67db-11e9-8398-fec52cf4a28e.png)






