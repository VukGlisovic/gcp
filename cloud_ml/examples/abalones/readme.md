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
feature column. Checkout `/trainer/train.py` for the full code.

In order to start a training job, we'll use the gcloud command line tool. This
will also automatically package our training application.

```bash
JOB_NAME="abalones_$(date +"%Y%m%d_%H%M%S")"
JOB_DIR="gs://abalone_xgboost_example/outputs"
TRAINING_PACKAGE_PATH="${HOME}/gcp/cloud_ml/examples/abalones/trainer/"
MAIN_TRAINER_MODULE="trainer.train"

gcloud ml-engine jobs submit training ${JOB_NAME} \
    --job-dir ${JOB_DIR} \
    --package-path ${TRAINING_PACKAGE_PATH} \
    --module-name ${MAIN_TRAINER_MODULE} \
    --region europe-west1 \
    --runtime-version=1.12 \
    --python-version=3.5 \
    --scale-tier BASIC \
    -- \
    --data_path=gs://abalone_xgboost_example/data/abalone_data.csv \
    --model_path=gs://abalone_xgboost_example/outputs/
```

