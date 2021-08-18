import csv
import os
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn import svm

def main():
    team_data = 'TeamData.csv'
    evidence, labels = load_data(team_data)
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=0.2
    )

    # Train model and make predictions
    logistic_regression_model = train_model(X_train, y_train, 1)
    naive_bayes_model = train_model(X_train, y_train, 2)
    knearest_neighbor_model = train_model(X_train, y_train, 3)
    random_forest_model = train_model(X_train, y_train, 4)
    svm_model = train_model(X_train, y_train, 5)

    evaluate(X_test, y_test, logistic_regression_model, 1)
    evaluate(X_test, y_test, naive_bayes_model, 2)
    evaluate(X_test, y_test, knearest_neighbor_model, 3)
    evaluate(X_test, y_test, random_forest_model, 4)
    evaluate(X_test, y_test, svm_model, 5)


def load_data(filename):
    evidence_list = []
    label_list = []

    with open(filename) as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            evidence_list.append([
                int(row['Matchday']),
                int(row['HomePositions']),
                int(row['AwayPositions']),
                int(row['HomeWins']),
                int(row['AwayWins']),
                int(row['HomeDraws']),
                int(row['AwayDraws']),
                int(row['HomeLosses']),
                int(row['AwayLosses']),
                int(row['HomeGoalsScored']),
                int(row['AwayGoalsScored']),
                int(row['HomeGoalsConceded']),
                int(row['AwayGoalsConceded']),
                int(row['HomeGoalDiff']),
                int(row['AwayGoalDiff']),
                int(row['HomePoints']),
                int(row['AwayPoints']),
                int(row['HomeSquadSize']),
                int(row['AwaySquadSize']),
                float(row['HomeAvgAge']),
                float(row['AwayAvgAge']),
                int(row['HomeNumForeigners']),
                int(row['AwayNumForeigners']),
                int(row['HomeAvgMarketVal']),
                int(row['AwayAvgMarketVal']),
                int(row['HomeMarketVal']),
                int(row['AwayMarketVal']),
            ])

            label_list.append(int(row['Result']))

    return (evidence_list, label_list)


def train_model(evidence, labels, type):
    """
    
    """
    model = None

    # Logistic Regression Model
    if type == 1:
        model = LogisticRegression(max_iter=10000).fit(evidence, labels)
    
    # Naive Bayes Model
    if type == 2:
        model = GaussianNB().fit(evidence, labels)

    # K-Nearest Neighbor Model
    if type == 3:
        model = KNeighborsClassifier(n_neighbors=1).fit(evidence, labels)

    # Random Forest Model
    if type == 4:
        model = DecisionTreeClassifier(random_state=1).fit(evidence, labels)

    # Support Vector Machine Model
    if type == 5:
        model = svm.SVC().fit(evidence, labels)

    return model


def evaluate(x_test, y_test, predictions, type):
    """
    
    """

    # Logistic Regression Predictions
    if type == 1:
        score = round(predictions.score(x_test, y_test), 2)
        print(f"Score for the logistic regression model: {score*100}%")
    
    # Naive Bayes Predictions
    if type == 2:
        score = round(predictions.score(x_test, y_test), 2)
        print(f"Score for the naive bayes model: {score*100}%")

    # K-Nearest Neighbor Predictions
    if type == 3:
        score = round(predictions.score(x_test, y_test), 2)
        print(f"Score for the K-Nearest neighbor model: {score*100}%")

    # Random Forest Predictions
    if type == 4:
        score = round(predictions.score(x_test, y_test), 2)
        print(f"Score for the random forest model: {score*100}%")

    # Support Vector Machine Predictions
    if type == 5:
        score = round(predictions.score(x_test, y_test), 2)
        print(f"Score for the support vector machine model: {score*100}%")
    

if __name__ == "__main__":
    main()