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

Now let's create a bucket where we can store the data and the outputs.
```bash
# create a bucket
gsutil mb -l europe-west1 gs://abalone_xgboost_example
# copy data to the bucket
gsutil cp ${HOME}/gcp/cloud_ml/examples/abalones/data/abalone_data.csv gs://abalone_xgboost_example/data/
```

For the data preprocessing, nothing too fancy has been done; no outliers were removed,
no extensive feature engineering has been done. We only one-hot encoded the 'Sex'
feature column.
