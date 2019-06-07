import re
import pandas as pd
import xlrd
import csv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# Count word and save to excel
def top_100_word_count_list_excel():
    data = open(r'../Document_Reports/Combined_Reports.txt', 'r', encoding='utf-8').read()
    #data = data.lower()
    #data = re.sub('\.\.+', '', data)
    #data = re.sub('\…\…+', '', data)
    #remove_special_chars = data.translate({ord(c): '' for c in "\.{2,}!@#$%^&*()[]\\{};:,./<>?\|`~-=_+\"\“\”"})
    #remove_special_chars = re.sub(r'[^a-zA-Z\s]+', '', remove_special_chars)
    stop_words = set(stopwords.words('english'))
    filtered_sentence = []
    word_tokens = word_tokenize(data)

    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)

    word_list = filtered_sentence
    wordfreq = {}

    for a in word_list:
        if a not in wordfreq:
            wordfreq[a] = 0
        wordfreq[a] += 1

    df = pd.DataFrame.from_dict(wordfreq, columns=['keyWords'], orient='index')
    writer = pd.ExcelWriter(r'../Documents_Top_100/Word_Count.xlsx')
    df.to_excel(writer, 'Sheet1')
    writer.save()
    print('=========== Word Count List : Excel File Printed Successfully ===========')


# getting CSV from Excel
def csv_from_excel():
    wb = xlrd.open_workbook(r'../Documents_Top_100/Word_Count.xlsx')
    sh = wb.sheet_by_name('Sheet1')
    your_csv_file = open(r'../Documents_Top_100/Word_Count.csv', 'w')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    your_csv_file.close()
    print('=========== Word Count List : CSV File Printed Successfully ===========')


# Main
if __name__ == '__main__':
    top_100_word_count_list_excel()
    csv_from_excel()
