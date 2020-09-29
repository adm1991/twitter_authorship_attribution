import tweepy
import csv
import string

#Twitter API credentials
consumer_key = #enter twitter API account details here 
consumer_secret = #enter twitter API account details here 
access_key = #enter twitter API account details here 
access_secret = #enter twitter API account details here 




#remove tweets with hashtags, remove mentions from tweets
def process_tweets(tweet_list):
    processed_tweets = []
    tweet_list = [tweets for tweets in tweet_list if "#" not
                  in tweets.full_text and not tweets.retweeted]
    #tweet_list = [tweet for tweet in tweet_list if len(tweet.entities['hashtags']) > 0]
    

    for tweet in tweet_list:
        tweet.full_text = str(tweet.full_text).encode('ascii', 'ignore').decode('utf8')
        tweet.full_text = [word.replace("&amp;", "&") for word in tweet.full_text.split(" ")
                           if not word.startswith(("@", "http")) and len(word) > 0]

        if len(tweet.full_text) > 4:
            tweet.full_text = ' '.join(word for word in tweet.full_text)
            processed_tweets.append(tweet)

        
    return processed_tweets
            



def get_all_tweets(screen_name):
        
    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    


    
    alltweets = []	
    new_tweets = api.user_timeline(screen_name = screen_name,
                                   count=200, tweet_mode='extended')
    
    alltweets.extend(process_tweets(new_tweets))      
    oldest = alltweets[-1].id - 1


    while len(new_tweets) > 10:
        print(len(new_tweets))
        print("Getting tweets before %s" % (oldest))
        new_tweets = api.user_timeline(screen_name = screen_name, count=200,
                                       max_id=oldest, tweet_mode='extended')

        
        alltweets.extend(process_tweets(new_tweets))
        oldest = alltweets[-1].id - 1
  
        print("...%s tweets downloaded so far" % (len(alltweets)))



    outtweets = [[screen_name, str(tweet.full_text)] for tweet in alltweets]

    #write the csv    
    with open('%s_tweets.csv' % screen_name, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "text"])
        writer.writerows(outtweets)


    pass

