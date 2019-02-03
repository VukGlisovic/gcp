# Training MNIST model with Cloud ML Engine

This example guides you through the steps required for training and serving an
MNIST model with the cloud ML engine.

A great notebook that will guide you through the steps, is
`02-mnist-model-with-cloudml-client.ipynb`. In this notebook, you will use the
python discovery client for the cloud ML engine to trigger a training job, create
a model, deploy a model version and request a prediction from the model that has
been deployed.

In the notebook the following steps are taken:

1. create a model<br/>
This will create a model in the cloud ML engine. However, this model will start
off empty. Thus not actual model is being served yet. We still have to create
this.
2. create a bucket in cloud storage<br/>
We'll store the train and test data, the model package and the training outputs
in this bucket.
3. package your training application<br/>
The training application must be packaged and uploaded to the cloud storage
bucket. We'll also upload the data here.
4. trigger a training job<br/>
Triggering a training job requires quite some configuration. We will trigger a
job using python version 3.5 and cloud ML runtime version 1.12.
5. optionally deploy your model in a docker container<br/>
We'll discuss this in more detail below.
6. create a model version<br/>
Deploy your model to the cloud ML engine.
7. request predictions<br/>
Use the cloud ml client to request predictions from the model that is being served
by the cloud ML engine.


### Deploy your Model in a Docker Container


```bash
docker run --rm -it -v ${HOME}/repository/gcp/cloud_ml/examples/mnist/models_for_serving:/models \
    -e MODEL_NAME=mnist \
    -e MODEL_PATH=/models/mnist \
    -p 8500:8500  \
    -p 8501:8501  \
    --name tensorflow-serving-example \
    tensorflow-serving-example:0.6
```
