# Using xgboost on Abalone Data

This example shows you how to train an xgboost model and serve it with the cloud
ml engine.

First let's get the data:
```bash
# general info on the data
curl https://archive.ics.uci.edu/ml/machine-learning-databases/abalone/abalone.names > info.txt

# the actual data
curl https://archive.ics.uci.edu/ml/machine-learning-databases/abalone/abalone.data > abalone_data.csv
```
