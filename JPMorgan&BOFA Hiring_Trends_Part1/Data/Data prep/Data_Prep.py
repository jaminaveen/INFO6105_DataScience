import pandas as pd


def read_csv(all_jobs_csv, count_csv, list_id):
    df_jp_morgan = pd.read_csv(all_jobs_csv, low_memory=False)
    list_url = df_jp_morgan['URL'].tolist()
    list_id = df_jp_morgan['job_id_list'].tolist()
    df_jp_morgan_text_count = pd.read_csv(count_csv)
    dfList = list(df_jp_morgan_text_count['keywords'])
    columns = list(df_jp_morgan.columns.values)

    final_list = []
    for i in dfList:
        for j in columns:
            if i == j:
                final_list.append(i)

    df_jp_morgan_final = df_jp_morgan[final_list]
    # print(df_jp_morgan_final.shape)
    df_jp_morgan_final['Institution'] = "JP MORGAN"
    df_jp_morgan_final['Job ID'] = list_id
    df_jp_morgan_final['Job URL'] = list_url
    df_jp_morgan_final["List ID"] = list_id
    cols = df_jp_morgan_final.columns.tolist()
    cols = cols[-4:] + cols[:-4]
    df_jp_morgan_final = df_jp_morgan_final[cols]
    print(df_jp_morgan_final.columns)

    return df_jp_morgan_final


def wordcountdictionaries(jobdescriptionwords):
    descdictionary = {}
    stopwords = open('long_stopwords.txt', 'r').read().split('\n')
    for word in jobdescriptionwords:
        if (word.isnumeric()) == False and (word not in stopwords):
            if word in descdictionary.keys():
                descdictionary[word] += 1
            else:
                descdictionary[word] = 1
    return descdictionary


def cleanandprepboa(keywordslocation, listid):
    boascrapeddf = pd.read_excel(r"..\Company_Job_Portal_Scraping_Generated_Files\BOAScrapeUrlwithDesc.xlsx")
    boolarray = boascrapeddf["Job Description"] != "Job Description:"
    boascrapeddfclean = boascrapeddf[boolarray]
    jobdescriptions = boascrapeddfclean['Job Description']
    boascrapeddfclean["Institution"] = "Bank of America"
    boascrapeddfclean["List ID"] = listid
    cols = boascrapeddfclean.columns.tolist()
    cols = cols[-2:-1] + cols[0:2] + cols[4:5]
    boascrapeddfclean = boascrapeddfclean[cols]
    # jobdescriptions

    desclist = []
    for jobdescription in jobdescriptions:
        jobDescriptionString = jobdescription.lower()
        remove_special_chars = jobDescriptionString.translate(
            {ord(c): '' for c in "\.•{2,}!@#$%^&*()[]\\{};:,./<>?\|`~-=_+\"\“\”"})
        word_list = remove_special_chars.split()
        desclist.append(word_list)

    listofdictionaries = []
    for jobdescription in desclist:
        listofdictionaries.append(wordcountdictionaries(jobdescription))
    wordcountfreqeachjobdf = pd.DataFrame(listofdictionaries)
    wordcountfreqeachjobdf = wordcountfreqeachjobdf.fillna(0)
    # wordcountfreqeachjobdf.to_csv("wordcountfreqeachjobdf.csv")
    columnnames = wordcountfreqeachjobdf.columns.values
    keywords = pd.read_csv(keywordslocation)
    requiredcolumns = []
    for word in keywords['keywords']:
        if word in columnnames:
            requiredcolumns.append(word)

    keywordcountineachurldf = wordcountfreqeachjobdf.loc[:, requiredcolumns]
    boascrapeddfcleandf = boascrapeddfclean.join(keywordcountineachurldf)
    return boascrapeddfcleandf

def combineJPmorganAndBOAdata(JPMorganDF,BOADF):
    combinedJPmorganAndBOAdata = JPMorganDF.append(BOADF)
    combinedJPmorganAndBOAdata = combinedJPmorganAndBOAdata.fillna(0)
    return combinedJPmorganAndBOAdata

# Main
if __name__ == '__main__':
    path = None
    df_1_JP_Morgan = read_csv(r'..\Company_Job_Portal_Scraping_Generated_Files\totalaggregate_final.csv', r'..\Documents_Top_100\100_word_count.csv', 1)
    df_2_JP_Morgan = read_csv(r'..\Company_Job_Portal_Scraping_Generated_Files\totalaggregate_final.csv', r'..\Documents_Top_100\100_TF_IDF.csv', 1)
    df_3_JP_Morgan = read_csv(r'..\Company_Job_Portal_Scraping_Generated_Files\totalaggregate_final.csv', r'..\Documents_Top_100\100_text_rank.csv', 3)
    df_1_Bofa = cleanandprepboa(r"..\Documents_Top_100\100_text_rank.csv", 3)
    df_2_Bofa = cleanandprepboa(r"..\Documents_Top_100\100_TF_IDF.csv", 2)
    df_3_Bofa = cleanandprepboa(r"..\Documents_Top_100\100_word_count.csv", 1)

    combinedWordCountresults = combineJPmorganAndBOAdata(df_1_JP_Morgan,df_3_Bofa)
    combinedTextRankresults = combineJPmorganAndBOAdata(df_3_JP_Morgan, df_1_Bofa)
    combinedTFIDFresults = combineJPmorganAndBOAdata(df_1_JP_Morgan, df_2_Bofa)

    combinedWordCountresults.drop(columns=['fintech.1',
                                          'fintech.2',
                                          'fintech.3',
                                          'connected.1',
                                          'connected.2',
                                          'connected.3']).to_csv(r"combinedWordCountresults.csv")
    combinedTextRankresults.drop(columns=['accessible', 'intelligence.1',
                                         'intelligence.2',
                                         'intelligence.3', ]).to_csv(r"combinedTextRankresults.csv")
    combinedTFIDFresults.to_csv(r"combinedtfidfresult.csv")
