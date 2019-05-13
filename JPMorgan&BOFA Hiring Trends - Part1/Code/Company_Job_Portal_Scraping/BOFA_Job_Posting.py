import urllib
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import xlsxwriter
import xlrd

browser = webdriver.Chrome(executable_path='../chromedriver/chromedriver.exe')
browser.get('http://careers.bankofamerica.com/search-jobs.aspx?c=united-states&r=us')
PAGE_XPATH = '//*[@id="PlhContentWrapper_dglistview"]/tbody/tr[12]/td/a[2]'
PAGE1_XPATH = '//*[@id="PlhContentWrapper_dglistview"]/tbody/tr[12]/td/a'


def read_csv():
    data = pd.read_csv(r'../Documents_Top_100/TF_IDF.csv', skiprows=1, names=["keyWords", "id", "freq"])
    keyWords = data["keywords"].tolist()
    count = 0
    top100 = []
    for i in keyWords:
        if count < 100:
            top100.append(i)
        else:
            break
        count += 1
    return top100


def get_href():
    table_id = browser.find_element_by_id('search-result').find_element_by_tag_name('table')
    rows = table_id.find_elements_by_tag_name("tr")  # get all of the rows in the table
    href = []
    # This loop is to loop through the job postings
    for row in rows:
        for col in row.find_elements_by_tag_name("td"):
            for link in col.find_elements_by_tag_name("a"):  # getting the hRef
                href.append(link.get_attribute('href'))
    return href


def get_job_desc(url):
    thePage = urllib.request.urlopen(url)
    data = BeautifulSoup(thePage, "html.parser")
    job_desc = data.find('div', {"id": "job-detail-wrapper"}).find('div', {"id": "job-detail"})
    return job_desc


countPage = 1
href_list = []
list_keywords = read_csv()
dict = {}
df1 = pd.DataFrame
workbook = xlsxwriter.Workbook('../Company_Job_Portal_Scraping_Generated_Files/BOAScrapeUrlwithDesc.xlsx', {'strings_to_urls': False})
worksheet = workbook.add_worksheet()
row = 1
column = 2
worksheet.write(0, 0, "Job ID")
worksheet.write(0, 1, "Job URL")
worksheet.write(0, 2, "Job Description")

while countPage >= 1 and countPage < 855:
    # href_list.append(get_href())
    link_count = 1
    for href in get_href():
        job_desc = ""
        jobDescDiv = get_job_desc(href)

        for para in jobDescDiv.findAll('p'):
            job_desc = job_desc + para.text
        avail_list = []
        # iteration in keyword list to find the count in jobdesc
        '''for keywords in list_keywords:
            if type(keywords) == str:
                freq = job_desc.count(keywords)
                dict.update({keywords: freq})
            #break'''
        if link_count >= 10:
            break
        link_count += 1
        column = 1
        worksheet.write(row, 0, href[44:52])
        worksheet.write(row, 1, href)
        worksheet.write(row, 2, job_desc)
        """for item in list(dict.values()):
            worksheet.write(row,0,href)
            worksheet.write(row, 1, jobDescDiv)
            column+=1"""
        row += 1

    # this condition will be the last block to change the page after all the scrapping operations
    if countPage == 1:
        element = browser.find_element_by_xpath(PAGE1_XPATH)
        browser.execute_script("arguments[0].click();", element)
    else:
        element = browser.find_element_by_xpath(PAGE_XPATH)
        browser.execute_script("arguments[0].click();", element)
    countPage += 1
print('\n'.join(map(str, href_list)))
workbook.close()

urldescdf = pd.read_excel('BOAScrapeUrlwithDesc.xlsx', header=0)

desclist = []
for i, row in urldescdf.iterrows():
    print(i)
    if (isinstance(row['Job Description'], str)):
        print(type(row['Job Description']))
        remove_special_chars = row['Job Description'].translate(
            {ord(c): '' for c in "\.•{2,}!@#$%^&*()[]\\{};:,./<>?\|`~-=_+\"\“\”"})
    else:
        remove_special_chars = ""
    word_list = remove_special_chars.split()
    desclist.append(word_list)

stopwords = open(r'../Stop_words/long_stopwords.txt', 'r').read().split('\n')


def wordcountdictionaries(jobdescriptionwords):
    descdictionary = {}
    for word in jobdescriptionwords:
        if (word.isnumeric()) == False and (word not in stopwords):
            if word in descdictionary.keys():
                descdictionary[word] += 1
            else:
                descdictionary[word] = 1
    return descdictionary


listofdictionaries = []
for jobdescription in desclist:
    listofdictionaries.append(wordcountdictionaries(jobdescription))

wordcountfreqeachjobdf = pd.DataFrame(listofdictionaries)

wordcountfreqeachjobdf = wordcountfreqeachjobdf.fillna(0)

wordcountfreqeachjobdf.to_excel("wordcountfreqeachjobdf.xlsx")

columnnames = wordcountfreqeachjobdf.columns.values


requiredcolumns = read_csv()

#urldescdf.drop('Job Description')


keywordcountineachurldf = wordcountfreqeachjobdf.loc[:, requiredcolumns]


urldescdf.join(keywordcountineachurldf).to_excel('BOAJobListWithKeywordCount.xlsx')

columnnames = wordcountfreqeachjobdf.columns.values

requiredcolumns = read_csv()

keywordcountineachurldf = wordcountfreqeachjobdf.loc[:, requiredcolumns]

urldescdfrequired=urldescdf.loc[:, ['Job ID', 'Job URL']]

urldescdfrequired.join(keywordcountineachurldf).to_excel('BOAJobListWithTextrankKeywordCount.xlsx')
