import pandas as pd
from boto3.s3.transfer import S3Transfer
import boto3
import io
import nltk
nltk.download('stopwords')
nltk.download('punkt')

nltk.download('wordnet')


def clustering_count():
    print('Feature Engineering beigns.....................................')
    aws_id = 'AKIAIBIGY3IWD3P7RAHA'
    aws_secret = 'aws_secret_access_key'

    # Reading the files from Amazon S3 - Word CLuster
    s3 = boto3.client('s3', aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
    obj = s3.get_object(Bucket='data-science-team1', Key='WordsClusters.xlsx')
    data = obj['Body'].read()
    samplekeywordclusters = pd.read_excel(io.BytesIO(data), encoding='ISO-8859-1')
    samplekeywordclusters = samplekeywordclusters.fillna("NA")

    print('Word Cluster file read from amazon S3 successfully')

    # Reading the job posting with count sheet from aws
    s3 = boto3.client('s3', aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
    obj = s3.get_object(Bucket='data-science-team1', Key='job_posting_with_count.csv')
    data = obj['Body'].read()
    keywordcount = pd.read_csv(io.BytesIO(data), encoding='ISO-8859-1')

    print('Job Posting with count file read from amazon S3 successfully')

    # Drop un-named column
    keywordcount.drop(columns=["Unnamed: 0"], inplace=True)

    def calculateclusterweightage(clusterlist, keywordcount, clustername):
        requiredcolumns = []
        for index, keywords in clusterlist.iteritems():
            if keywords in keywordcount.columns:
                requiredcolumns.append(keywords)
        clusterweightagedf = pd.DataFrame()
        keywordsColumns = keywordcount[requiredcolumns]
        keywordsColumns = keywordsColumns.astype('int64')
        clusterweightagedf[clustername] = keywordsColumns.sum(axis=1)
        return clusterweightagedf

    clusterweightage = pd.DataFrame()
    clusterweightage1 = pd.DataFrame()
    clusterweightage = calculateclusterweightage(samplekeywordclusters["PAYMENTS"], keywordcount, "PAYMENTS")
    clusterweightage1 = calculateclusterweightage(samplekeywordclusters["BLOCKCHAIN"], keywordcount, "BLOCKCHAIN")
    clusterweightage2 = calculateclusterweightage(samplekeywordclusters["TRADING AND INVESTMENTS"], keywordcount, "TRADING AND INVESTMENTS")
    clusterweightage3 = calculateclusterweightage(samplekeywordclusters["PLANNING"], keywordcount, "PLANNING")
    clusterweightage4 = calculateclusterweightage(samplekeywordclusters["LENDING"], keywordcount, "LENDING")
    clusterweightage5 = calculateclusterweightage(samplekeywordclusters["INSURANCE"], keywordcount, "INSURANCE")
    clusterweightage6 = calculateclusterweightage(samplekeywordclusters["BIG DATA AND ANALYTICS"], keywordcount, "BIG DATA AND ANALYTICS")
    clusterweightage7 = calculateclusterweightage(samplekeywordclusters["SECURITY"], keywordcount, "SECURITY")
    clusterweightage8 = calculateclusterweightage(samplekeywordclusters["FINANCE"], keywordcount, "FINANCE")

    finalclustersweightage = clusterweightage.join(clusterweightage1).join(clusterweightage2).join(clusterweightage3).join(clusterweightage4).join(clusterweightage5).join(clusterweightage6).join(clusterweightage7).join(
        clusterweightage8)

    list = []
    a = finalclustersweightage.idxmax(axis=1)
    i = 0
    finalclustersweightage[finalclustersweightage > 0] = int(0)
    for index, row in finalclustersweightage.iterrows():

        if 'PAYMENTS' == a[i]:
            row['PAYMENTS'] = 1

        if 'BLOCKCHAIN' == a[i]:
            row['BLOCKCHAIN'] = 1

        if 'TRADING AND INVESTMENTS' == a[i]:
            row['TRADING AND INVESTMENTS'] = 1

        if 'PLANNING' == a[i]:
            row['PLANNING'] = 1

        if 'LENDING' == a[i]:
            row['LENDING'] = 1

        if 'INSURANCE' == a[i]:
            row['INSURANCE'] = 1

        if 'BIG DATA AND ANALYTICS' == a[i]:
            row['BIG DATA AND ANALYTICS'] = 1

        if 'SECURITY' == a[i]:
            row['SECURITY'] = 1
        if 'FINANCE' == a[i]:
            row['FINANCE'] = 1

        i += 1

    is_fintech = finalclustersweightage.idxmax(axis=1)
    is_fintechlist = []
    for i in is_fintech:
        if i != "FINANCE":
            is_fintechlist.append(1)
        else:
            is_fintechlist.append(0)

    payments_list = finalclustersweightage['PAYMENTS'].tolist()
    insurance_list = finalclustersweightage['INSURANCE'].tolist()
    blockchain_list = finalclustersweightage['BLOCKCHAIN'].tolist()
    planning_list = finalclustersweightage['PLANNING'].tolist()
    lending_list = finalclustersweightage['LENDING'].tolist()
    big_data_list = finalclustersweightage['BIG DATA AND ANALYTICS'].tolist()
    security_list = finalclustersweightage['SECURITY'].tolist()
    trading_list = finalclustersweightage['TRADING AND INVESTMENTS'].tolist()
    finance_list = finalclustersweightage['FINANCE'].tolist()
    keywordcount['PAYMENTS'] = payments_list
    keywordcount['INSURANCE'] = insurance_list
    keywordcount['BLOCKCHAIN'] = blockchain_list
    keywordcount['PLANNING'] = planning_list
    keywordcount['LENDING'] = lending_list
    keywordcount['BIG DATA AND ANALYTICS'] = big_data_list
    keywordcount['TRADING AND INVESTMENTS'] = trading_list
    keywordcount['SECURITY'] = security_list
    keywordcount['TRADITIONAL FINANCE TERMS'] = finance_list
    keywordcount['IS FINTECH'] = is_fintechlist
    keywordcount = keywordcount.drop(keywordcount.columns[keywordcount.columns.str.contains('unnamed', case=False)], axis=1)

    keywordcount.to_csv("fintech_keywordcount_with_feature_engineering.csv")

    print('Final sheet with Job posting and its categorical distribution is successfully generated')

    client = boto3.client('s3', aws_access_key_id='AKIAIBIGY3IWD3P7RAHA', aws_secret_access_key='aws_secret_access_key')
    transfer = S3Transfer(client)
    transfer.upload_file('fintech_keywordcount_with_feature_engineering.csv', 'data-science-team1', 'fintech_keywordcount_with_feature_engineering.csv')
    print('Final sheet with Job posting and its categorical distribution is successfully transferred to Amazon S3')
    # print(df_with_required_count.sum(axis=0))
    print('==========================Below are the urls of analysis============================')
    print('Top 24 hiring trends:' + 'https://public.tableau.com/profile/akshara.singh#!/vizhome/BanksHiring/Sheet1')
    print('FinTech Job Hiring Trend:' + 'https://public.tableau.com/profile/akshara.singh#!/vizhome/FintechJobHiringTrend/Sheet1')
    print('Company with most and least jobs in different category:' + 'https://public.tableau.com/profile/akshara.singh#!/vizhome/HighestLowestJobCount/Sheet1')
    print('Category with most and least jobs:' + 'https://public.tableau.com/profile/akshara.singh#!/vizhome/JobCountByFintechCategories/JobCountByFintechCategories')
    print('Fintech to Non Fintech Job ratio across top 24 banks: https://datawrapper.dwcdn.net/4Xn7X/1/')
    print('Top jobs in each bank: https://public.tableau.com/profile/akshara.singh#!/vizhome/TopJobByBank-1/Dashboard1')


# Main
if __name__ == '__main__':
    clustering_count()
