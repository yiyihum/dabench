import pandas as pd

# Load the training and test datasets
train_data = pd.read_csv('/workspace/train.csv')
test_data = pd.read_csv('/workspace/test.csv')

# Display the first few rows of the training and test datasets
print(train_data.head())
print("---")
print(test_data.head())
