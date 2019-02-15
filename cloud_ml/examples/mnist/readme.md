# Training MNIST Model with Cloud ML Engine

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

This section is based on Yu Ishikawa his
<a href="https://github.com/yu-iskw/tensorflow-serving-example">article</a>.
Basically, we're taking the following steps here to serve our model:
1. clone the github repository<br/>
```bash
git clone git@github.com:yu-iskw/tensorflow-serving-example.git
```
This repository will make sure we can build the docker image we need for serving
the model.

2. build the docker image<br/>
```bash
docker build --rm -f Dockerfile -t tensorflow-serving-example:0.6 .
```
Builds a docker image from a dockerfile where `--rm` means remove intermediate
containers after a successful build, `-f` (relative) path to the dockerfile and
`-t` the name and optionally a tag of the image.

3. create a directory named `models_for_serving`<br/>
This directory will be a shared volume with the container that will be started
later on. Create the following directory structure:
```bash
# copy the variables folder and the graph protocol buffer
mkdir -p ./models_for_serving/mnist/1
cp -r ./outputs/export/mnist/[TIMESTAMP]/* ./models_for_serving/mnist/1/

# The file structure should look like this now
models_for_serving/
└── mnist
    └── 1
        ├── saved_model.pb
        └── variables
            ├── variables.data-00000-of-00001
            └── variables.index
```

4. start your container<br/>
```bash
docker run --rm -it -v ${HOME}/gcp/cloud_ml/examples/mnist/models_for_serving:/models \
    -e MODEL_NAME=mnist \
    -e MODEL_PATH=/models/mnist \
    -p 8500:8500  \
    -p 8501:8501  \
    --name tensorflow-serving-example \
    tensorflow-serving-example:0.6
```
This will start a docker container and directly serve your model. `-v` mounts a
volume to the docker container. `-e` sets environment variables. `-p` forwards
docker ports to the hosts ports. `--name` of the container. `--rm` removes the
container when it exits. `-it` basically starts an interactive bash shell in the
container.

5. request prediction from your container<br/>
Use a grpc client to request predictions. You can use the `tools/grpc_client.py`
to request predictions.
