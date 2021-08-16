import csv

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

def main():
    team_data = 'TeamData.csv'
    evidence, labels = load_data(team_data)
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=0.4
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


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


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    return model.fit(evidence, labels)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    true_count, false_count = 0, 0
    sensitivity_count, specificity_count = 0, 0

    for label, prediction in zip(labels, predictions):
        if label:
            true_count += 1
            if prediction:
                sensitivity_count += 1
        else:
            false_count += 1
            if not prediction:
                specificity_count += 1

    sensitivity = sensitivity_count / true_count
    specificity = specificity_count / false_count
        

    return (sensitivity, specificity)

if __name__ == "__main__":
    main()