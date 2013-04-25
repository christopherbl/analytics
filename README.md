twitter-mining: 
Stores Twitter results in a SQL Server database for a list of search terms (any combination of hashtags, handles, keywords) Also included is a text mining process that can extract data and predict retweet likelihood by training and testing a model based on words in tweets (bag of words with TF-IDF). 

This project contains two files: 

Twitter.py: 		
Python code that uses urllib to return Twitter search results and pymssql to populate SQL Server database (db must be created first, see instructions at bottom)

TwitterRTPublish:	
RapidMiner (ver 5.3.008) process file in xml format which can be loaded into RapidMiner using File-Import Process.  As the www.rapidminer.com site states, RapidMiner is the world-leading open-source system for data mining - it allows the user to quickly apply different data mining algorithms against the twitter data with no coding required. 

You will need the following software: 
- Python 2.7
- RapidMiner 5 including Text Mining extension (Weka extension to use those data mining models, Web Mining extension if Twitter link text mining required)
- SQL Server (Express) 

This project shows that one does not need much code to use Python to pull search results from Twitter and SQL Server (Express version is free) to persist the results.  RapidMiner (community edition is free) can then be used to analyze/text mine the results – this project just creates a model to predict/analyze retweet content but you may want to extract twitter http link content, via the Get Pages and Extract Content operators, and add that to the text mining for potentially better results.  You could also overlay sentiment analysis or analyze influential retweeters instead.

The decision tree models allow for better interpretability (you can see what words influenced retweets the most) but Naive Bayes or other models may give you better prediction results.  In RapidMiner, just right click on model operator and select Replace Operator to try out other data mining algorithms.

The Python code to populate the SQL Server database with Twitter search results is probably best run using a task scheduler as it needs to run hourly/daily if any of the search terms return many results (Twitter search only returns the last 1500 results over no more than the last week or so).  I tried both Twython and Twitter Python APIs but neither worked for searching correctly - the Twitter Python API worked until late March 2013 but then started failing whenever the rpp parameter was populated.

Not shown in this project is the need to split the Tweets table that the Python code populates into a TweetsTraining table and a TweetsTest table; the former would train/create the model (all of the RapidMiner operators that connect up to the Validation operator) and the latter would be used to test the model with tweets it has not seen.   If dealing with tens of thousands or more tweets, you would probably want to use ETL (can leverage the logic used in the Read Database operator) within SQL Server to randomly create these two tables from the Tweets data, as the SQL query in RapidMiner would start taking a while to run.

Before using the Read Database operator in RapidMiner, make sure you have installed the JTDS driver from http://jtds.sourceforge.net/ and followed the directions at http://www.linglom.com/2009/03/28/enable-remote-connection-on-sql-server-2008-express/ to set up the SQL Server Browser Service, SQL Server Network Configuration, and instance properties correctly.

The two SQL Server tables can be created using SQL Server CREATE TABLE with following parameters (first one in each table is primary key):

Tweets

[tweet_id] [BIGINT] NOT NULL,
[tweet_datetime] [datetime] NOT NULL,
[tweet_keyword] [VARCHAR](50) NULL,
[tweet] [VARCHAR](200) NOT NULL,
[tweeter] [VARCHAR](MAX) NULL,
[tweeter_id] [BIGINT] NOT NULL,
[lang] [VARCHAR](50) NULL

Log

[run_id] [INT] NOT NULL,
[run_datetime] [datetime] NOT NULL,
[tweets_stored] [INT] NOT NULL,


