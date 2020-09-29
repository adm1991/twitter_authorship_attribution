import numpy as np
from nltk import ngrams
from nltk import FreqDist
from collections import Counter
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn.preprocessing import Normalizer



#load raw data from .csv file. Store each tweet as a list, containing a userID and the tweet body
with open("data.csv", "r") as raw_data:
    raw_data = [lines.rstrip(",").split(",", 1) for lines in raw_data.read().splitlines()]

#Only retain tweets longer than 3 characters in length. 
    data_filtered = [line for line in raw_data if len(line[1].split()) > 3]


#create dictionary containing usernames and their associated numerical ID, and a dictionary containing UserID's and a list of their associated tweets. 
tweets_dictionary = {k[0]: [] for k in data_filtered}
labelsdict = dict(zip(tweets_dictionary, [i for i in range(50)]))
for items in data_filtered:
    tweets_dictionary[items[0]].append(items[1:])
    

#Define the Data object used to create input for the classifier. 
class Vector():
    def __init__(self, m):
        self.features = np.zeros((50, m))
        self.labels = np.zeros(50)
    
    def set_features(self, i, value):
        self.features[i] = value
        
    def set_labels(self, i, value):
        self.labels[i] = value
        
    def get_features(self):
        return self.features
    
    def get_labels(self):
        return self.labels
       
    
    

#generate a list of the most m most frequent ngrams across the entireity of the training data. 
def generate_most_frequent_ngrams(n, m):
    ngrams_list = []  
    most_frequent_ngrams_dict = {k : [] for k in tweets_dictionary}
    
    for usernames in tweets_dictionary:
        for entries in tweets_dictionary[usernames]:
            ngrams_list.extend(list(ngrams(entries[0], n)))
            most_frequent_ngrams_dict[usernames].extend(list(ngrams(entries[0], n)))
    return [items[0] for items in FreqDist(ngrams_list).most_common(m)]



#generate the most frequent ngrams in the training data (first 80% of tweets for each user) and testing data (last 20% of tweets for each user)
def generate_user_ngrams(username, n):
    training_data = []
    testing_data = []
    
    for entries in tweets_dictionary[username][0:(int(0.8*len(tweets_dictionary[username])))]:
        training_data.extend(list(ngrams(entries[0], n)))
    for entries in tweets_dictionary[username][(int(0.8*len(tweets_dictionary[username]))):]:
        testing_data.extend(list(ngrams(entries[0], n)))
        
    return training_data, testing_data



#generate vector object for training and testing data for each user. n = length of ngram, m = length of vector (defined as frequency with which 
# m most frequent ngrams in whole dataset) appear in the tweets of each user.
def generate_vectors(username, frequent_ngrams, training_vector, testing_vector, n, m):

    
    ngrams_count_dict = {k : 0 for k in frequent_ngrams}
    data = generate_user_ngrams(username, n)
    
    training = data[0]
    testing = data[1]
    
    training_freq = Counter(training)
    for items in frequent_ngrams:
        if items in training:
            ngrams_count_dict[items] = training_freq[items]
        else:
            ngrams_count_dict[items] = 0
    features_vector = np.array(list(ngrams_count_dict.values()))
    
    training_vector.set_features(labelsdict[username], features_vector)
    training_vector.set_labels(labelsdict[username], labelsdict[username])
    
    testing_freq = Counter(testing)
    for items in frequent_ngrams:
        if items in testing:
            ngrams_count_dict[items] = testing_freq[items]
        else:
            ngrams_count_dict[items] = 0
    features_vector = np.array(list(ngrams_count_dict.values()))
    
    testing_vector.set_features(labelsdict[username], features_vector)
    testing_vector.set_labels(labelsdict[username], labelsdict[username])
         
    
    
#fit linearSVM classifier to the training vectors, and fit on testing vectors. 
def classify(n, m):
    frequent_ngrams = generate_most_frequent_ngrams(n, m)
    training_vector = Vector(m)
    testing_vector = Vector(m)
    
    usernames = list(tweets_dictionary.keys())
    
    for items in usernames:
        generate_vectors(items, frequent_ngrams, training_vector, testing_vector, n, m)
        

    x_train = training_vector.get_features()
    y_train = training_vector.get_labels()
    x_test = testing_vector.get_features() 
    y_test = testing_vector.get_labels()

    



    classifier =  Pipeline([
       ('Normalizer', Normalizer(copy=True, norm='l2')),
        ('classifier', LinearSVC()),
    ])
    
    classifier.fit(x_train, y_train)
    y_pred = classifier.predict(x_test)
    
    print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
    


classify(3, 300)

   
    
