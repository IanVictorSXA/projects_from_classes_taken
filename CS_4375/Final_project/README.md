Final project for Introduction to Machine Learning 

Doing sentiment analysis on stock market data (stock tweets and financial news headlines)

Simple binary classification problem: 1 for positive texts and -1 for negative texts.

Used 2 datasets from kaggle (see all-data and stock_data files)

feature_extraction_visualization file:

    - Uploaded datasets
    - one of the datasets contained 3 classes (neutral texts), so all the rows associated with neutral class were erased
    - then the datasets were concatenated
    - then performed data extraction
    - used visualization tool to explore data
    - created the final 3 datasets for learning (bow, itidf, and trigram)

naive_bayes file:

    - trained multinomial naive bayes
    - used 5 fold cross-validation
    - 20% of each dataset was saved for testing 
    - since only one hyperparemeter was used, there is a graph showing the performance for each hyperparameter value
    - after finding best hyperparameter value, trained best model on the entire training set and measure performance
    - there are 3 confusion matrices at the end of notebook

logReg file:

    - trained logistic regression
    - used 5 fold cross-validation
    - 20% of each dataset was saved for testing 
    - after finding best hyperparameter value, trained best model on the entire training set and measure performance
    - there are 3 confusion matrices at the end of notebook

all-data - dataset of financial news headline
stock-data - dataset of stock tweets

Name of the datasets created  (they were not uploaded for being too big):

    bow - bag of words dataset
    tfidf - text frequency inverse document frequency dataset
    trigram - 3-gram dataset


Websites used:

https://www.kaggle.com/code/aashkatrivedi/feature-extraction-for-sentiment-analysis

https://scikit-learn.org/stable/modules/feature_extraction.html

https://www.kaggle.com/datasets/yash612/stockmarket-sentiment-dataset

https://www.kaggle.com/datasets/ankurzing/sentiment-analysis-for-financial-news
