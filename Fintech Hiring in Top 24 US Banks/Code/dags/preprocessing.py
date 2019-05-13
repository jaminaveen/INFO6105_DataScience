import pandas as pd
import re
import boto3
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from boto3.s3.transfer import S3Transfer
import io

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')


def data_cleaning():
    # have all the variables populated which are required below
    new_list_job_description = []
    lemmatized_description = []

    # Getting the all teams job posting file from Amazon S3
    aws_id = 'AKIAIBIGY3IWD3P7RAHA'
    aws_secret = 'aws_secret_access_key'

    s3 = boto3.client('s3', aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
    obj = s3.get_object(Bucket='data-science-team1', Key='all_job_posting.csv')
    data = obj['Body'].read()
    all_job_data = pd.read_csv(io.BytesIO(data), encoding='ISO-8859-1')

    print('All job posting file read successful from amazon S3')

    # Copy the read csv into a new data frame
    all_job_data_copy = all_job_data
    all_job_data_copy.reset_index(drop=True, inplace=True)

    # Description column of the data frame is converted into a list
    list_job_description = all_job_data['Description'].tolist()

    # Removing special characters from the list and converting it to lowercase
    for i in list_job_description:
        a = re.sub('[^A-Za-z]+', ' ', str(i))
        a = a.lower()
        new_list_job_description.append(a)

    # Removing stop words
    new_list_job_description = [word for word in new_list_job_description if word not in stopwords.words('english')]

    # Adding SPLITHEREAFTERLEMMATIZATION at the end of each column
    combined_description_data = " SPLITHEREAFTERLEMMATIZATION ".join(new_list_job_description)

    # lemmatizing words
    lmtzr = WordNetLemmatizer()
    a = combined_description_data.split(' ')
    for i in a:
        word_after_lammatize = lmtzr.lemmatize(i)
        lemmatized_description.append(word_after_lammatize)

    print('Job Posting lemmatization successful')

    lemmatized_description_join = " ".join(lemmatized_description)
    description_df = pd.DataFrame({"Job Description": lemmatized_description_join.split('SPLITHEREAFTERLEMMATIZATION')})

    descr_lemmatizes_data_frame = all_job_data_copy.join(description_df)
    descr_lemmatizes_data_frame = descr_lemmatizes_data_frame.drop(columns="Description")
    descr_lemmatizes_data_frame = descr_lemmatizes_data_frame.dropna()

    descr_lemmatizes_data_frame.to_csv("descrlemmatizesdataframeclean.csv")
    all_job_data['Description'] = new_list_job_description
    job_description_list_descr_lemmatizes_data_frame = descr_lemmatizes_data_frame['Job Description'].tolist()

    # df = pd.read_excel("Words_for_Clustering - copy.xlsx")
    # df = df.dropna()

    # Converting the 100 words list to  lowercase, removing special characters, lammetizing
    s3 = boto3.client('s3', aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
    obj = s3.get_object(Bucket='data-science-team1', Key='Final100Keywords.xlsx')
    data = obj['Body'].read()
    word_list = pd.read_excel(io.BytesIO(data), encoding='ISO-8859-1')

    print('100 keywords file read successful from amazon S3')

    # lemmatized_clean_word_list: List of clean word list
    clean_word_list = []
    for key, i in word_list['Keywords'].iteritems():
        a = re.sub('[^A-Za-z]+', ' ', str(i))
        a = a.lower()
        clean_word_list.append(a)
    lemmatizer = WordNetLemmatizer()
    lemmatized_clean_word_list = []
    for word in clean_word_list:
        a = []
        for each in word.split(" "):
            a1 = lemmatizer.lemmatize(each)
            a.append(a1.lower())
        a = " ".join(a)
        lemmatized_clean_word_list.append(a)
    # print(lemmatized_clean_word_list)

    # Counting the numbers of words in each description : one-gram, bi-gram, tri-grams
    list_of_counts = []
    for list_ in job_description_list_descr_lemmatizes_data_frame:
        matched_words = {}
        words = nltk.word_tokenize(list_)
        words_set = set(words)
        bi_grams = nltk.bigrams(words)
        trigr = nltk.trigrams(words)

        bi_grams_pairs = [' '.join(pair) for pair in bi_grams]

        bi_grams_pairs_set = set(bi_grams_pairs)
        trigram_pairs = [' '.join(each) for each in trigr]
        trigram_pairs_set = set(trigram_pairs)
        # count = 0

        matched_words.update({word: words.count(word) for word in words_set if word in lemmatized_clean_word_list})
        matched_words.update({bi: bi_grams_pairs.count(bi) for bi in bi_grams_pairs_set if bi in lemmatized_clean_word_list})
        matched_words.update({tri: trigram_pairs.count(tri) for tri in trigram_pairs_set if tri in lemmatized_clean_word_list})
        list_of_counts.append(matched_words)

    df_with_required_count = pd.DataFrame(list_of_counts)

    # with_count_data_frame: Final data frame with jobs and their count
    with_count_data_frame = descr_lemmatizes_data_frame.join(df_with_required_count)
    with_count_data_frame = with_count_data_frame.fillna(0)

    # appending all the remaining rows with the genearted dataframe

    remainingwords = []
    duplicatedf = with_count_data_frame.loc[:, "access":"wealth management"]
    duplicatedf = duplicatedf.columns.values.tolist()
    word_list = word_list["Keywords"].tolist()
    for each in word_list:
        if each not in duplicatedf:
            remainingwords.append(each)
    for i in remainingwords:
        with_count_data_frame[i] = float(0)

    # with_count_data_frame.to_csv(r'A:\2nd Semester\Data Science\Assignment 2\Anurag\FINAL\word_count.csv')

    print('Job posting Word Count file successful')
    # return with_count_data_frame

    with_count_data_frame.to_csv("job_posting_with_count.csv")
    client = boto3.client('s3', aws_access_key_id='AKIAIBIGY3IWD3P7RAHA', aws_secret_access_key='aws_secret_access_key')
    transfer = S3Transfer(client)
    transfer.upload_file('job_posting_with_count.csv', 'data-science-team1', 'job_posting_with_count.csv')
    # transfer.upload_file('with_count_data_frame.csv', 'data-science-team1', 'with_count_data_frame' + "/" + 'with_count_data_frame')
    print('Job posting file transferred to S3 successful')

    # print(df_with_required_count.sum(axis=0))
    # return [df_with_required_count, all_job_data]


# Main
if __name__ == '__main__':
    data_cleaning()
