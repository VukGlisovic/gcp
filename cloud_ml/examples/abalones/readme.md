# Using xgboost on Abalone Data

This example shows you how to train an xgboost model and serve it with the cloud
ml engine.


### Get the Data

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


### Start a Training Job

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


### Test Model with Local Predictions

This section explains how you can check whether your model is fit for serving
with the cloud ML engine and to get a preview of what the response of the cloud
ML engine is going to be. It also saves unnecessary costs if your model is not
doing as you expect.

Note that you might need a python 2 environment to execute the command below.
You could create an environment with:

```bash
conda create -n "local-predict" xgboost tensorflow
```

If required, activate this environment and execute the following:

```bash
gcloud ml-engine local predict \
    --model-dir gs://abalone_xgboost_example/outputs/ \
    --json-instances ${HOME}/gcp/cloud_ml/examples/abalones/tools/abalone_examples.txt \
    --framework XGBOOST
```

You should get a response that looks similar to:

```bash
[10.558841705322266, 8.467399597167969, 11.20057201385498, 10.883077621459961, 9.557068824768066]
```


### Deploy Model

It's time to serve your model with the cloud ML engine. The cloud ML engine
has `model`s and `version`s. A `model` is a container for `version`s. Let's
first create a model:

```bash
gcloud ml-engine models create "predict_abalone_rings"
```

And create your first version for this model:

```bash
# note that --model must be the model you just created
gcloud ml-engine versions create "xgboost_regressor_$(date +"%Y%m%d_%H%M%S")" \
    --model predict_abalone_rings \
    --origin gs://abalone_xgboost_example/outputs/ \
    --runtime-version=1.12 \
    --framework XGBOOST \
    --python-version=3.5
```


### Request Prediction

Let's finish it off by requesting a prediction from our freshly deployed model.

```bash
# leave --version, this will make sure it uses the default version to predict with
gcloud ml-engine predict \
    --model predict_abalone_rings \
    --json-instances ${HOME}/gcp/cloud_ml/examples/abalones/tools/abalone_examples.txt
```

This will yield a response similar to when requesting predictions with gcloud
local predict.

Bravo! Your model is being served!
