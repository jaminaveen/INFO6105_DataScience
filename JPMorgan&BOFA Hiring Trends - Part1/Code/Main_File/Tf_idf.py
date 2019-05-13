from sklearn.feature_extraction.text import TfidfVectorizer

import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import xlrd
import csv
import nltk
import pandas as pd

nltk.download('stopwords')


def remove_string_special_characters(s):
    print(s)

    stripped = re.sub('[^\w\s]', ' ', s)
    stripped = re.sub('_', ' ', stripped)
    stripped = re.sub(',', ' ', stripped)
    stripped = re.sub('\s+', ' ', stripped)
    stripped = stripped.strip()

    return stripped


def top_100_Tf_Idf_list_excel():
    merged_text = open(r'../Document_Reports/Combined_Reports.txt', 'r', encoding='utf-8').read()
    removed_sp_char = remove_string_special_characters(merged_text)

    removed_sp_char_lowered = removed_sp_char.lower()
    stop_words = set(stopwords.words('english'))
    filtered_sentence = []
    word_tokens = word_tokenize(removed_sp_char_lowered)
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)

    print(filtered_sentence)

    filtered_sentence_string = ' '.join(filtered_sentence)

    tfidf = TfidfVectorizer()

    response = tfidf.fit_transform([filtered_sentence_string])

    feature_names = tfidf.get_feature_names()
    tfidfwithscores = []
    for col in response.nonzero()[1]:
        print(feature_names[col], ' - ', response[0, col])
        tfidfwithscores.append([feature_names[col], response[0, col]])

    # df = pd.DataFrame([feature_names, response])

    tfidfwithscores = pd.DataFrame(tfidfwithscores)
    tfidfwithscoressorted = tfidfwithscores.sort_values(by=[1], ascending=False)
    tfidfwithscoressorted.to_excel(r'../Documents_Top_100/TF_IDF.xlsx')
    print('=========== TF IDF Count List : EXCEL File Printed Successfully ===========')


def csv_from_excel():
    wb = xlrd.open_workbook(r'../Documents_Top_100/TF_IDF.xlsx')
    sh = wb.sheet_by_name('Sheet1')
    your_csv_file = open(r'../Documents_Top_100/TF_IDF.csv', 'w', newline='')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    your_csv_file.close()
    print('=========== TF IDF Count List : CSV File Printed Successfully ===========')


# Main
if __name__ == '__main__':
    merged_text = None
    top_100_Tf_Idf_list_excel()
    csv_from_excel()
