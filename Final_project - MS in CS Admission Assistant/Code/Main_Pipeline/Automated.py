import pandas as pd
from dask.multiprocessing import get
import pandas as pd
import os
from bs4 import BeautifulSoup
import re



'''
This method is used to clean the data 
'''
def cleaning(abc):

    allfileslist = os.listdir(r'C:\Users\anura\Downloads\Machine-Learning-Model-for-Graduate-Admission-master\Machine-Learning-Model-for-Graduate-Admission-master/Data/HTML FILES/')
    combined_csv = pd.concat([pd.read_csv(r'C:\Users\anura\Downloads\Machine-Learning-Model-for-Graduate-Admission-master\Machine-Learning-Model-for-Graduate-Admission-master/Data/HTML FILES/' + f) for f in allfileslist])
    combined_csv.loc[combined_csv['status'] == 'acccept', "status"] = "accept"
    # filtering out empty records
    combined_csv = combined_csv.loc[~(combined_csv['links'] == "[]"), :]
    # removing empty records
    combined_csv.drop(columns='Unnamed: 0', inplace=True)
    combined_csv.reset_index(drop=True, inplace=True)
    combined_csv.loc[combined_csv.loc[:,
                     'university_name'] == "illinois_institute_of_technology_accept", "university_name"] = "illinois_institute_of_technology"
    combined_csv.loc[combined_csv.loc[:,
                     'university_name'] == "university of california, irvine", "university_name"] = "university_of_california_irvine"
    combined_csv.loc[
        combined_csv.loc[:, 'university_name'] == "clemson_university_accept", "university_name"] = "clemson_university"
    combined_csv.loc[
        combined_csv.loc[:, 'university_name'] == "clemson_university_reject", "university_name"] = "clemson_university"
    # unwrapping stored html pages and extracting features from html tags
    html_pages = combined_csv.links.tolist()
    temp = []

    for i in html_pages:
        soup = BeautifulSoup(i)
        a = soup.find_all('div', class_='col-sm-4 col-xs-4')
        temp_inside = []
        for x in a:
            k = (x.h4.text)
            t = [j for j in k.strip().split("\n") if len(j) is not 0]
            temp_inside.append(t)
        temp.append(temp_inside)

    all = []
    for each in temp:
        list = []
        for i in each:
            for j in i:
                list.append(j)
        all.append(list)

    # we will make a new dataframe with extracted information from html pages and it's corresponding university name and status
    university_list = combined_csv.university_name.tolist()
    status_list = combined_csv.status.tolist()

    combined_df = pd.DataFrame(all)
    combined_df['university_name'] = university_list
    combined_df['status'] = status_list

    # naming our features
    list_columns = ['gre_score', 'droping', 'gre_score_quant', 'gre_score_verbal', 'test_score_toefl', 'droping_1',
                    'undergraduation_score', 'work_ex', 'papers_published', 'droping_3', 'university_name', 'status']
    combined_df.columns = list_columns
    combined_df.drop(columns=['droping', 'droping_1', 'droping_3'], inplace=True)

    # filling work experience and work_ex with zero, considering when there are no values given
    combined_df = combined_df.fillna(0)

    '''
    Cleaning Column data
    Removing Null values
    Removing noise
    Conversion of % and 10 pinter score in CGPA to 4 pointer
    Toefl and IELTS score to the same scale according to the information available 
    on ETS Official website (https://www.ets.org/toefl/institutions/scores/compare/)
    '''

    def replace_special_chars(i):
        # a = re.sub('[^A-Za-z]+',' ',str(i))
        a = re.findall(r'\d+', str(i))
        # a = a.lower()
        return ''.join(a)

    combined_df['gre_score'] = combined_df.gre_score.apply(replace_special_chars)
    combined_df['gre_score_quant'] = combined_df['gre_score_quant'].apply(replace_special_chars)

    combined_df['test_score_toefl'] = combined_df['test_score_toefl'].apply(replace_special_chars)
    combined_df['gre_score_verbal'] = combined_df['gre_score_verbal'].apply(replace_special_chars)
    combined_df['work_ex'] = combined_df['work_ex'].apply(replace_special_chars)

    combined_df["undergraduation_score"] = [x.replace('CGPA', '') for x in combined_df["undergraduation_score"]]
    combined_df["undergraduation_score"] = [x.replace('%', '') for x in combined_df["undergraduation_score"]]
    combined_df["papers_published"] = [str(x).replace('Tech Papers', '') for x in combined_df["papers_published"]]

    combined_df.loc[combined_df['work_ex'] == '', 'work_ex'] = 0

    values = []
    for each in combined_df.undergraduation_score.unique():
        try:
            float(each)
        except:
            values.append(each)

    for each in values:
        combined_df = combined_df[combined_df.undergraduation_score != each]

    combined_df[
        ['gre_score', 'gre_score_quant', 'gre_score_verbal', 'test_score_toefl', 'undergraduation_score', 'work_ex']] = \
    combined_df[['gre_score', 'gre_score_quant', 'gre_score_verbal', 'test_score_toefl', 'undergraduation_score',
                 'work_ex']].apply(pd.to_numeric)

    combined_df = combined_df.loc[~(combined_df.test_score_toefl.isna()), :]

    combined_df.reset_index(drop=True, inplace=True)

    # combined_df.to_csv('pipeline_input.csv')
    print("in cleaning function")
    return combined_df
'''
Cleaning method ends
'''

'''
method to convert percentage and cgpa into scale of 4.0
'''
def calculateCgpa(cleaning):
    dataset = cleaning
    listing = dataset['undergraduation_score'].tolist()
    update_cgpa_score_scale_4 = []
    for score in listing:
        s = 0
        try:
            score = float(score)

        except:
            score = float(score)

        if score > 10:
            s = ((score) / 20) - 1

            s = round(s, 2)
            update_cgpa_score_scale_4.append(s)
        else:
            s = ((score) / 10) * 4

            s = round(s, 2)
            update_cgpa_score_scale_4.append(s)

    dataset['undergraduation_score'] = update_cgpa_score_scale_4
    print("in gpa function")
    return dataset

'''
Method to rank the universities
'''
def rankingUniversity(dataset):
    required_colleges = ['northeastern_university', 'illinois_institute_of_technology',
                         'michigan_technological_university', 'rochester_institute_of_technology',
                         'university_of_southern_california', 'north_carolina_state_university_raleigh',
                         'university_of_texas_arlington', 'university_of_texas_dallas', 'syracuse_university',
                         'clemson_university', 'new_york_university', 'indiana_university_bloomington',
                         'rutgers_university_new_brunswick', "---", 'university_of_florida',
                         'carnegie_mellon_university', 'georgia_institiute_of_technology',
                         'university_of_colorado_boulder', 'university_of_north_carolina_at_charlotte',
                         'university_of_iowa', 'university_of_connecticut', 'worcester_polytechnic_institute', '---',
                         'kansas_state_university', 'university_of_cincinnati', 'university_of_maryland_college_park',
                         'university_of_california_irvine', 'texas_a_m_university_college_station',
                         'state_university_of_new_york_at_stony_brook', 'george_mason_university',
                         'university_of_texas_austin']
    required_colleges_ranking = [15, 97, 117, 66, 19, 49, 64, 52, 118, 89, 22, 48, 25, 150, 62, 1, 9, 58, 30, 71, 70,
                                 79, 76, 115, 130, 10, 23, 31, 35, 59, 16]
    dictionary_req_college = dict(zip(required_colleges, required_colleges_ranking))

    dataset['ranking'] = dataset['university_name']
    dataset['ranking'].replace(dictionary_req_college, inplace=True)
    print("in ranking function")
    return dataset

'''
Method to convert IELTS to scale of TOEFL
'''
def ToeflIelts(rankingUniversity):
    dataset = rankingUniversity
    dataset.loc[dataset['test_score_toefl'] < 9, 'test_score_toefl'] = pd.cut(
        dataset.loc[dataset['test_score_toefl'] < 9, 'test_score_toefl'],
        bins=[-1, 0.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9],
        labels=[0, 31, 34, 45, 59, 78, 93, 101, 109, 114, 117, 120])
    print("in toefl function")
    return dataset
'''
Method to rank the papers published 
'''
def paperPublish(ToeflIelts):
    dataset = ToeflIelts
    temp_list=[]
    for x in dataset["papers_published"]:
        x=str(x)
        x = x.replace('None','0')
        x = x.replace('NA','0')
        x = x.replace('nan','0')
        x = x.replace('International','3')
        x = x.replace('National','2')
        x = x.replace('Local','1')
        temp_list.append(x)
    dataset["papers_published"]=temp_list
    dataset.to_csv("final_dataset.csv")
'''
Task Creation
'''
def runDask():
    dsk={'Task0':(cleaning,"default"),
         'Task1':(calculateCgpa,'Task0'),
         'Task2':(rankingUniversity,'Task1'),
         'Task3':(ToeflIelts,'Task2'),
         'Task4': (paperPublish, 'Task3')}
    get(dsk, 'Task4')

if __name__ == "__main__":
    runDask()