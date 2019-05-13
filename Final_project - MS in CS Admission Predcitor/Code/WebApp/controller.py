import pandas as pd
import h2o
import boto3
from io import StringIO
import s3fs
import pickle
import numpy as np
from dask.multiprocessing import get
from sklearn.preprocessing import StandardScaler

# Method to connect AWS S3
def connectaws():
    aws_id = 'aws_id'
    aws_secret = 'aws_access_key_id'
    s3 = boto3.client('s3', aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
    return s3

# Method to get list of the Universities
def get_universities():
    univ = pd.read_csv(r"data/university_list.csv")
    univ_dict = univ.to_dict(orient="records")
    return univ_dict

# Method to get the profile of applicant during login with emailId and Password
def get_student_details(name, password):
    all_student = read_student_details()
    stud = all_student[all_student['email'].isin([name])& all_student['password'].isin([password])]
    return stud

# Method to read the student details from Amazon S3 and returns the student dataframe
def read_student_details():
    bucket = "gradschoolpredictor"
    file_name = "student_details.csv"

    s3 = connectaws()
    obj = s3.get_object(Bucket=bucket, Key=file_name)
    # get object and file (key) from bucket

    student_details = pd.read_csv(obj['Body'], index_col=0)  # 'Body' is a key word that will get the body of the csv
    # student_details = pd.read_csv(r"data/student_details.csv", index_col=0) #This line will get the details from local file
    return student_details

# Method to save Student Profile into AWS S3
def save_student_details(student):
    student_df = read_student_details()
    student_df= student_df.append(student, ignore_index=True)
    stud = student_df[student_df['email'].isin([student['email']]) & student_df['password'].isin([student['password']])]
    write_csv(student_df)
    return stud

# Method to write CSV into Amazon S3
def write_csv(student_df):
    bucket = "gradschoolpredictor"
    file_name = "student_details.csv"

    bytes_to_write = student_df.to_csv(None).encode()
    fs = s3fs.S3FileSystem(key='aws_id', secret='aws_access_key_id')
    with fs.open('s3://gradschoolpredictor/student_details.csv', 'wb') as f:
        f.write(bytes_to_write)

# Hethod to get the list of students applied to NEU
def get_university_student_applied_list():
    stud = pd.read_csv(r"data/FinalDataSetNortheastern.csv")
    return stud

#This method is used by university to predict the student getting admit
def get_univ_model(stud_df):
    model_path = r'model/university_random_forest_predict.pickel'
    with open(model_path, 'rb') as handle:
        model = pickle.load(handle)
    # loading the scalar function from pickel file to scale the input dataframe
    scalar_path = r'data/UniversityRFstandardScaler_rf_model.pickel'
    with open(scalar_path, 'rb') as handle:
        scalar = pickle.load(handle)
    term_hotencoded = pd.get_dummies(stud_df[['term_applying']])
    stud_df = pd.concat([stud_df, term_hotencoded], axis=1)
    # stud_df = stud_df.drop(columns=['term_applying']).join(pd.get_dummies(stud_df,columns=['term_applying'], prefix='term_applying'))
    print(stud_df.columns)
    to_feed_df = stud_df[['gre_score_quant','gre_score_verbal','test_score_toefl','undergraduation_score','work_ex', 'papers_published']]

    predictions = model.predict(scalar.transform(to_feed_df))
    return predictions

# This method is used to convert percentage and CGPA out of 10 to CGPA out of 4
def to_cgpa(ielts_to_toefl):
    student_df = ielts_to_toefl
    score =student_df.iloc[0]["ugscore"]
    mode = student_df.iloc[0]["ugmode"]
    s = 0
    try:
       score = float(score)
    except:
       score= 0
    if mode == 'ugscore_perc':
       s = ((score)/20) - 1
       s = round(s,2)
       student_df["undergraduation_score"]= s
    else:
       s = ((score)/10)*4
       s = round(s,2)
       student_df["undergraduation_score"] = s
    return student_df

# This method is used to scale the ielts score to toefl equivalent
def ielts_to_toefl(df_student):
    if df_student.iloc[0]['english_mode'] == 'ielts' :
        score  = float(df_student.english_score)
        if score <= 9.0:
            eng_score = np.array([score],dtype=float)
            df_student['test_score_toefl'] =pd.cut(eng_score, bins=[-1,0.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9], labels=[0,31,34,45,59,78,93,101,109,114,117,120])
        else:
            df_student['test_score_toefl'] = df_student.english_score
    else:
        df_student['test_score_toefl'] = df_student.english_score
    return df_student
'''
Task Creation
'''
def runDask(df_student):
    dsk={'Task0':(ielts_to_toefl,df_student),
         'Task1':(to_cgpa,'Task0')}
    stud_df = get(dsk, 'Task1')
    return stud_df


# Method used by student to predict chance of getting admit from University based on university choice and model
def student_admit_predict(df_student,model_name):
    # loading the model from the pickel file
    if model_name == "Bagging":
        model_path = r'model/student_university_bagging_classifier_predict.pickel'
        with open(model_path, 'rb') as handle:
            model = pickle.load(handle)
        # loading the scalar function from pickel file to scale the input dataframe
        scalar_path = r'data/standard_scaler_bagging_model.pickel'
        with open(scalar_path, 'rb') as handle:
            scalar = pickle.load(handle)
    elif model_name == "RandomForest":
        model_path=r'model/student_university_random_forest_predict.pickel'
        with open(model_path, 'rb') as handle:
            model = pickle.load(handle)
        # loading the scalar function from pickel file to scale the input dataframe
        scalar_path = r'data/standard_scaler_rf_model.pickel'
        with open(scalar_path, 'rb') as handle:
            scalar = pickle.load(handle)
    elif model_name == 'KNN':
        model_path = r'model/student_university_kNN_bagging_classifier_predict.pickel'
        with open(model_path, 'rb') as handle:
            model = pickle.load(handle)
        # loading the scalar function from pickel file to scale the input dataframe
        scalar_path = r'data/standard_scaler_kNN_bagging_model.pickel'
        with open(scalar_path, 'rb') as handle:
            scalar = pickle.load(handle)
    elif model_name== "H2O":
        model_path=r'model/StackedEnsemble_AllModels_AutoML_20190421_184847'

    # creating the dataframe to predict the result
    column_list = ["gre_score","gre_score_quant","gre_score_verbal","test_score_toefl","undergraduation_score","work_ex","papers_published","ranking"]
    student_df_to_predict = pd.DataFrame(columns=column_list)
    student_df_to_predict['gre_score'] = df_student['gre']
    student_df_to_predict['gre_score_quant'] = df_student['gre_quants']
    student_df_to_predict['gre_score_verbal'] = df_student['gre_verbal']
    student_df_to_predict['test_score_toefl'] = df_student['test_score_toefl'].astype(float)
    student_df_to_predict['undergraduation_score'] = df_student['undergraduation_score']
    student_df_to_predict['work_ex'] = df_student['workex']
    student_df_to_predict['papers_published'] = df_student['papers_published']
    univ_rank, univ = get_univ_ranking(df_student['university_choice'])
    student_df_to_predict['ranking'] = univ_rank
    student_df_to_predict= student_df_to_predict.apply(pd.to_numeric)
    if model_name != "H2O":  # for manual models
        predictions = model.predict(scalar.transform(student_df_to_predict))
        return predictions[0]
    else: # for H2O model
        h2o.init()
        saved_model = h2o.load_model(model_path)
        test_frame= h2o.H2OFrame(student_df_to_predict)
        predictions = saved_model.predict(test_frame)
        predictions = predictions.as_data_frame()
        return predictions.iloc[0]["predict"]

# Method to get the ranking of the university
def get_univ_ranking(univ_name):
    univ_df = pd.read_csv(r'data/ranking.csv')
    univ_dict ={}
    for index, row in univ_df.iterrows():
        univ_dict[row[0]] = univ_dict.get(row[0], row[1])
    univ_rank = univ_dict.get(univ_name[0])
    return univ_rank, univ_dict

#Method used by student to know the list of recommended univeristy
def student_admit_recommend(df_student):
    model_path = r'model/student_university_bagging_classifier_predict.pickel'
    with open(model_path, 'rb') as handle:
        model = pickle.load(handle)

        scalar_path = r'data/standard_scaler_bagging_model.pickel'
    with open(scalar_path, 'rb') as handle:
        scalar = pickle.load(handle)

    column_list = ["gre_score", "gre_score_quant", "gre_score_verbal", "test_score_toefl", "undergraduation_score",
                   "work_ex", "papers_published", "ranking"]
    student_df_to_append = pd.DataFrame(columns=column_list)
    student_df_to_append['gre_score'] = df_student['gre']
    student_df_to_append['gre_score_quant'] = df_student['gre_quants']
    student_df_to_append['gre_score_verbal'] = df_student['gre_verbal']
    student_df_to_append['test_score_toefl'] = df_student['test_score_toefl'].astype(float)
    student_df_to_append['undergraduation_score'] = df_student['undergraduation_score']
    student_df_to_append['work_ex'] = df_student['workex']
    student_df_to_append['papers_published'] = df_student['papers_published']
    univ_rank, univ = get_univ_ranking(df_student['university_choice'])
    student_df_to_recommend = pd.DataFrame(columns=column_list)
    for i in range(0,29):
        student_df_to_recommend = student_df_to_recommend.append(student_df_to_append)
    student_df_to_recommend['ranking'] = list(univ.values())

    prediction = pd.DataFrame(model.predict_proba(scalar.transform(student_df_to_recommend)),
                 columns=['accept', 'reject'])
    prediction['Universities'] = list(univ.keys())
    prediction['Ranking'] = list(univ.values())
    prediction['accept']= (prediction['accept']*100).astype(int)
    prediction = prediction.loc[(prediction['accept'])>55,:]
    best_pred = prediction.sort_values(by=['Ranking'], ascending=True).head(6)
    best_pred = best_pred.sort_values(by=['accept'], ascending=False)
    return best_pred
