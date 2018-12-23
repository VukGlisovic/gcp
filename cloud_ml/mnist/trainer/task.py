import logging
import argparse
import model as m
import tensorflow as tf


parser = argparse.ArgumentParser()
parser.add_argument('--learning_rate',
                    help='Learning rate for the optimizer.',
                    type=float,
                    default=0.0001)
parser.add_argument('--model_dir',
                    help='Output directory for storing checkpoints and model.',
                    type=str,
                    default='~/gcp/cloud_ml/mnist/outputs')

known_args, _ = parser.parse_known_args()
learning_rate = known_args.learning_rate
model_dir = known_args.model_dir


def run():
    params = dict(learning_rate=learning_rate)
    classifier = tf.estimator.Estimator(model_fn=m.model_fn,
                                        model_dir=model_dir,
                                        params=params)


if __name__ == '__main__':
    logging.info("Starting training.")
    run()
