from bs4 import BeautifulSoup
import pandas as pd
import requests
import re


def company_job_posting_link():
    job_posting_link = []
    for i in range(1, 250):
        url = 'https://jobs.jpmorganchase.com/ListJobs/All/sortdesc-jobtitle/Page-' + str(i)
        print('------------------######### PAGE : ' + str(i) + '##########---------------------')
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        links_with_text = []
        for a in soup.find_all('a', href=True):
            if a.text:
                links_with_text.append(a['href'])
        # print(links_with_text)
        r = re.compile('ShowJob.*')
        newlist = filter(r.search, links_with_text)
        for i in newlist:
            job_posting_link.append('https://jobs.jpmorganchase.com' + str(i))
            job_posting_link = list(set(job_posting_link))
    return job_posting_link


def jp_morgan_word_count(list_links):
    for url in list_links:
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        a = [el.get_text() for el in soup.find_all('div', attrs={"class": 'desc'})]
        b = soup.find_all('div', {'class': 'req'})
        for x in b:
            text_jobid = x.get_text()
            text_jobid = text_jobid[7:]
            job_id_list.append(text_jobid)
            str_list = ''.join(a)
            str_list = str_list.lower()
            remove_special_chars = str_list.translate(
                {ord(c): '' for c in "\.•{2,}!@#$%^&*()[]\\{};:,./<>?\|`~-=_+\"\“\”"})
            f_list = remove_special_chars.split()

            dictionary_each_page_word(f_list, url)

    dictionary_each_page_word_print(dict_words_each_page_url, job_id_list, dict_words_each_page_words)


def dictionary_each_page_word(f_list, url):
    dict_empty = {}
    for i in f_list:
        if i not in dict_empty:
            dict_empty[i] = 0
        dict_empty[i] += 1
    dict_words_each_page_words.append(dict_empty)
    dict_words_each_page_url.append(url)


def dictionary_each_page_word_print(dict_words_each_page_url, job_id_list, dict_words_each_page_words):
    df_page = pd.DataFrame(dict_words_each_page_words)
    df_page['URL'] = dict_words_each_page_url
    df_page['job_id_list'] = job_id_list
    df_page.to_excel(r'..\Company_Job_Portal_Scraping_Generated_Files\JP_Morgan_all pages.xlsx')


if __name__ == '__main__':
    dict_words_each_page = {}
    dict_words_each_page_words = []
    dict_words_each_page_url = []
    job_id_list = []
    links = company_job_posting_link()
    jp_morgan_word_count(links)
