import urllib
import json
import pymssql
import sys
from datetime import datetime

print "RUNNING Twitter search to pull back full list of search terms"
conn = pymssql.connect(host='hostname',  user='sa', password='pword', database='Twitter')
cur = conn.cursor()
# initialize run ID so we can write that plus one for this run
cur.execute("SELECT ISNULL(MAX(run_id),0) FROM Log")
run = cur.fetchone()[0]+1

# twitter_search API seemed to stop working as of late March 2013
#twitter_search = twitter.Twitter(domain="search.twitter.com")
# need double quotes around multiple word exact search terms
search_list = ['"job post"','#hiring','#tweetmyjobs','job']
stored = 0
# get latest tweet ID from last run so we don't bother going back beyond then with new searching
cur.execute("SELECT ISNULL(MAX(tweet_id),0) FROM Tweets")
latest_tweet_id = cur.fetchone()[0]
# step through each search_term to pull all results from Twitter search
for search_term in search_list:
    match_result = 0
    page = 1
    search_results = []
    # loop for each page of search results - stop if we get to tweet ID from last run (avoid wasting rate limited calls to Twitter search)
    while (page <= 15) and (match_result == 0):
        print search_term+" and page = "+str(page)+ " and stored = "+str(stored)
        # as of march 27, seems that rpp= parameter causes twitter api search to fail, remove ",rpp=100" for time being
        #search_results.append(twitter_search.search(q=search_term, page=page))
        result = {'errors':0}
        # continue trying to run search if error occurs as spurious error occurs from call sometimes
        while 'errors' in result:
            search = urllib.urlopen("http://search.twitter.com/search.json?q="+search_term+"&rpp=100&page="+str(page))
            result = json.loads(search.read())
        # add search results from latest call
        search_results.append(result)
        # cycle through each tweet in page of results
        for tweet in search_results[page-1]['results']:
            # only load from last tweet ID of last run (means new search terms added to search_list will only go back to datetime/tweet ID of last run)
            if tweet['id'] <= latest_tweet_id:
                match_result = 1
            else:
                #print tweet['text'].encode('utf-8')
                # do not store tweet if already stored in table - needed since different search_terms may bring back same tweet
                subq0 = "SELECT COUNT(*) FROM Tweets WHERE tweet_id = '"+str(tweet['id_str'].encode('utf-8'))+"'" 
                cur.execute(subq0)  
                if cur.fetchone()[0] == 0:
                    try:
                        # insert single tweet in our table
                        subq1 = "INSERT INTO Tweets (tweet_id, tweet_datetime, tweet, tweeter, tweeter_id, lang) VALUES ("
                        subq2 = str(tweet['id_str'].encode('utf-8'))+", "
                        subq3 = "CAST(SUBSTRING('"+str(tweet['created_at'].encode('utf-8'))+"',5,21) AS DATETIME), "
                        subq4 = "'"+str(tweet['text'].encode('utf-8').replace('\'','').replace(';',''))+"', "
                        subq5 = "'"+str(tweet['from_user'].encode('utf-8'))+"', "
                        subq6 = str(tweet['from_user_id_str'].encode('utf-8'))+", "
                        subq7 = "'"+str(tweet['iso_language_code'].encode('utf-8'))+"')"
                        subq8 = subq1+subq2+subq3+subq4+subq5+subq6+subq7
                        cur.execute(subq1+subq2+subq3+subq4+subq5+subq6+subq7)
                        conn.commit()
                        stored = stored + 1
                    except:
                        print "*** Error:", sys.exc_info()[0], "***"
        page = page + 1
# insert log table entry
subq1 = "INSERT INTO Log (run_id, run_datetime, tweets_stored) VALUES ("
subq2 = str(run)+", "
subq3 = "CAST(SUBSTRING('"+str(datetime.now())+"',1,19) AS DATETIME), "
subq4 = str(stored)+")"
subq5 = subq1+subq2+subq3+subq4
cur.execute("SET IDENTITY_INSERT Log ON")
cur.execute(subq1+subq2+subq3+subq4)
cur.execute("SET IDENTITY_INSERT Log OFF")
conn.commit()
conn.close()
