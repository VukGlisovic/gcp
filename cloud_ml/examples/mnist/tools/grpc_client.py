"""This script is based on a tensorflow serving example at
https://github.com/yu-iskw/tensorflow-serving-example/blob/master/python/grpc_mnist_client.py

It's a python grpc client for generating predictions.
"""

import argparse
import time
import numpy as np

import grpc
from tensorflow.contrib.util import make_tensor_proto

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc


def run(host, port, image_filepath, model, signature_name):

    channel = grpc.insecure_channel('{host}:{port}'.format(host=host, port=port))
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

    # Read an image
    data = np.load(image_filepath)
    data = data.reshape((1, 28, 28, 1))
    data = data.astype(np.float32) / 255.

    start = time.time()

    # Call classification model to make prediction on the image
    request = predict_pb2.PredictRequest()
    request.model_spec.name = model
    request.model_spec.signature_name = signature_name
    request.inputs['input'].CopyFrom(make_tensor_proto(data, dtype=np.float32, shape=[1, 28, 28, 1], verify_shape=True))

    result = stub.Predict(request, 10.0)

    end = time.time()
    time_diff = end - start

    # Reference:
    # How to access nested values
    # https://stackoverflow.com/questions/44785847/how-to-retrieve-float-val-from-a-predictresponse-object
    print('time elapased: {}'.format(time_diff))
    print(result)
    print('')
    print('Predicted class: {}'.format(result.outputs['classes'].int64_val))
    print('Probabilities: {}'.format(result.outputs['probabilities'].float_val))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='Tensorflow server host name', default='localhost', type=str)
    parser.add_argument('--port', help='Tensorflow server port number', default=8500, type=int)
    parser.add_argument('--image_filepath', help='input image of digit', type=str)
    parser.add_argument('--model', help='model name', type=str)
    parser.add_argument('--signature_name', help='Signature name of saved TF model',
                        default='serving_default', type=str)

    args = parser.parse_args()
    run(args.host, args.port, args.image_filepath, args.model, args.signature_name)
