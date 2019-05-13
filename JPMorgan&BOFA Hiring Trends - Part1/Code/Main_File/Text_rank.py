
import re
from summa import keywords
import pandas as pd

data = open(r'../Document_Reports/Combined_Reports.txt', 'r', encoding='utf-8').read()
partialclean = data.split()
partialclean = ' '.join(partialclean)
#print(partialclean)
#cleantext = partialclean.lower()
# printable = set(string.printable)
# text = list(filter(lambda x: x in printable, text)) #filter funny characters, if any.
# text = [' '.join(e for e in text if e.isalnum())]
cleantext = re.sub('\W+', ' ', partialclean)

stopwordcontents = open(r'../Stop_words/long_stopwords.txt', 'r').read()
stopwordsadd = stopwordcontents.split('\n')
addstopwords = ' '.join(stopwordsadd)

keywords = keywords.keywords(cleantext, ratio=0.2, words=None, language="english", split=False, scores=False,
                             deaccent=False, additional_stopwords=addstopwords)
keywordsDescOrder = keywords.split('\n')
keywordsdf = pd.DataFrame({'keyWords': keywordsDescOrder})
keywordsTxtRank_DescOrderCSV = keywordsdf.to_csv(r'../Documents_Top_100/Text_Rank.csv',index=None)
