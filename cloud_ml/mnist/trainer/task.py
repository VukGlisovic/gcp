import os
import logging
import argparse
import model as m
import tensorflow as tf

logging.basicConfig(level=logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument('--features_file',
                    help='Filepath where features for training are contained (these should correspond to the labels file).',
                    type=str,
                    default='../data/train/features.tfrecord')
parser.add_argument('--labels_file',
                    help='Filepath where labels for training are contained (these should correspond to the features file).',
                    type=str,
                    default='../data/train/labels.tfrecord')
parser.add_argument('--model_dir',
                    help='Output directory for storing checkpoints and model.',
                    type=str,
                    default=os.path.join(os.environ['HOME'], 'gcp/cloud_ml/mnist/outputs/'))
parser.add_argument('--learning_rate',
                    help='Learning rate for the optimizer.',
                    type=float,
                    default=0.0001)

known_args, _ = parser.parse_known_args()
features_file = known_args.features_file
labels_file = known_args.labels_file
model_dir = known_args.model_dir
learning_rate = known_args.learning_rate
logging.info("Input parameters:")
logging.info("Features filepath: %s", features_file)
logging.info("Labels filepath: %s", labels_file)
logging.info("Output directory: %s", model_dir)
logging.info("Learning rate: %s", learning_rate)


def run():
    params = dict(learning_rate=learning_rate)
    logging.info("Creating mnist classification model.")
    classifier = tf.estimator.Estimator(model_fn=m.model_fn,
                                        model_dir=model_dir,
                                        params=params)
    logging.info("Starting training of mnist model.")
    classifier.train(input_fn=lambda: m.input_fn(features_file, labels_file, epochs=1, batch_size=32, buffer_size=50))
    logging.info("Evaluate accuracy of the model.")
    classifier.evaluate(input_fn=lambda: m.input_fn('../data/test/features.tfrecord', '../data/test/labels.tfrecord', epochs=1, batch_size=50, buffer_size=0))


if __name__ == '__main__':
    run()
