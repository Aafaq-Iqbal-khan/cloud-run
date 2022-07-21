# import libraries
from flask import Flask, render_template, request
from newsapi import NewsApiClient
from gnews import GNews
import pandas as pd
from newspaper import Article
import os
from newspaper import Config
import nltk
# nltk.download('punkt')


# authentic websites
irish_authentic_websites= ['Independent.ie', 'Irish Mirror','Irish Central', 'Irish Times','The Irish Times' , 'TheJournal.ie', 'RT News', 'BreakingNews.ie', 'Reuters UK', 'rte news']
world_authentic_websites= ['Bloomberg', 'The Guardian', 'MIT Technology Review', 'CNBC', 'Forbes', 'Gulf Business', 'World Economic Forum', 'Business Wire','MarketWatch', 'Reuters']

# init flask app
app = Flask(__name__)

google_news = GNews(language='en', country='IE', period='1d')
news = google_news.get_news('AI OR data') # A list of dict
df=pd.DataFrame(news)
#df=df[:5]

# user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
# config = Config()
# config.browser_user_agent = user_agent

list1=[]
for ind in df.index:
    dict={}
    article = Article(df['url'][ind])
    try:
      article.download()
      article.parse()
    except:
      print('***FAILED TO DOWNLOAD***', article.url)
      continue

    article.nlp()
    dict['Date']=df['published date'][ind]
    dict['Website']=df['publisher'][ind].title
    dict['Title']=df['title'][ind]
    dict['link']=df['url'][ind]
    dict['Article']=article.text.replace('\n','')
    dict['Summary']=article.summary.replace('\n','')
    # dict['Description'] = article.description.replace('\n', '')
    dict['Keywords']=article.keywords
    dict['urltoimage']=article.top_image
    dict['author'] = article.authors
    list1.append(dict)

news_df=pd.DataFrame(list1)
# remove those news whose artciles were not downloaded
news_df = news_df[news_df['Article']!='']
# replace unavailable authers name with "Not Available"
for ind in news_df.index:
  if(news_df['author'][ind]==[]):
    news_df['author'][ind]="Not Available"
  else:
      news_df['author'][ind] = news_df['author'][ind][0]

news_df['indicator']=news_df['Website'].isin(irish_authentic_websites)
df1=news_df[news_df['indicator']==True]
df2=news_df[news_df['indicator']==False]
df2['indicator']=df2['Website'].isin(world_authentic_websites)
df3=df2[df2['indicator']==True]
df4=df2[df2['indicator']==False]

a=df1.append(df3)
final_df=a.append(df4)
final_df
final_news=final_df.to_dict('records')

# Init news api
# newsapi = NewsApiClient(api_key='70fdb9ba81ba40b6bda148e672898bd9')

# helper function
# def get_sources_and_domains():
# 	all_sources = newsapi.get_sources()['sources']
# 	sources = []
# 	domains = []
# 	for e in all_sources:
# 		id = e['id']
# 		domain = e['url'].replace("http://", "")
# 		domain = domain.replace("https://", "")
# 		domain = domain.replace("www.", "")
# 		slash = domain.find('/')
# 		if slash != -1:
# 			domain = domain[:slash]
# 		sources.append(id)
# 		domains.append(domain)
# 	sources = ", ".join(sources)
# 	domains = ", ".join(domains)
# 	return sources, domains

@app.route('/')
def home():
    return  render_template('home.html', articles = final_news)


if __name__ == "__main__":
	app.run(debug = True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
