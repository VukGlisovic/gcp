import logging
import argparse
import model as m
import tensorflow as tf


parser = argparse.ArgumentParser()
parser.add_argument('--features_file',
                    help='Filepath where features for training are contained (these should correspond to the labels file).',
                    type=str,
                    default='../data/train/features.tfrecord')
parser.add_argument('--labels_file',
                    help='Filepath where labels for training are contained (these should correspond to the features file).',
                    type=str,
                    default='../data/train/labels.tfrecord')
parser.add_argument('--learning_rate',
                    help='Learning rate for the optimizer.',
                    type=float,
                    default=0.0001)
parser.add_argument('--model_dir',
                    help='Output directory for storing checkpoints and model.',
                    type=str,
                    default='~/gcp/cloud_ml/mnist/outputs')

known_args, _ = parser.parse_known_args()
features_file = known_args.features_file
labels_file = known_args.labels_file
learning_rate = known_args.learning_rate
model_dir = known_args.model_dir


def run():
    params = dict(learning_rate=learning_rate)
    classifier = tf.estimator.Estimator(model_fn=m.model_fn,
                                        model_dir=model_dir,
                                        params=params)
    classifier.train(input_fn=lambda: m.input_fn(features_file, labels_file, epochs=1, batch_size=32, buffer_size=50))


if __name__ == '__main__':
    logging.info("Starting training.")
    run()
