import os
import logging
import argparse
from .model import model_fn, input_fn
import tensorflow as tf

logging.basicConfig(level=logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument('--train_data_folder',
                    help='Path to folder containing the training data. This folder should have '
                         'two files: features.tfrecord and labels.tfrecord',
                    type=str,
                    default='../data/train/')
parser.add_argument('--evaluation_data_folder',
                    help='Path to folder containing the evaluation data. This folder should likewise'
                         'containt two files.',
                    type=str,
                    default='')
parser.add_argument('--model_dir',
                    help='Output directory for storing checkpoints and model.',
                    type=str,
                    default=os.path.join(os.environ['HOME'], 'gcp/cloud_ml/examples/mnist/outputs/'))
parser.add_argument('--nr_epochs',
                    help='Number of times to iterate over the entire dataset.',
                    type=float,
                    default=1)
parser.add_argument('--learning_rate',
                    help='Learning rate for the optimizer.',
                    type=float,
                    default=0.0001)

known_args, _ = parser.parse_known_args()
train_data_folder = known_args.train_data_folder
evaluation_data_folder = known_args.evaluation_data_folder
model_dir = known_args.model_dir
nr_epochs = known_args.nr_epochs
learning_rate = known_args.learning_rate
logging.info("Input parameters:")
logging.info("Train data folder filepath: %s", train_data_folder)
logging.info("Evaluation data folder filepath: %s", evaluation_data_folder)
logging.info("Output directory: %s", model_dir)
logging.info("Number of epochs: %s", nr_epochs)
logging.info("Learning rate: %s", learning_rate)


def run():
    """Execute training and evaluation of the model for classifying
    mnist data.
    """
    params = dict(learning_rate=learning_rate)
    logging.info("Creating mnist classification model.")
    classifier = tf.estimator.Estimator(model_fn=model_fn,
                                        model_dir=model_dir,
                                        params=params)

    logging.info("Starting training of mnist model.")
    logging.info("You can checkout tensorboard with the following command:\ntensorboard --logdir='%s'", model_dir)
    train_features_file = os.path.join(train_data_folder, 'features.tfrecord')
    train_labels_file = os.path.join(train_data_folder, 'labels.tfrecord')
    classifier.train(input_fn=lambda: input_fn(train_features_file, train_labels_file, epochs=nr_epochs, batch_size=32, buffer_size=50))

    if evaluation_data_folder:
        logging.info("Evaluate accuracy of the model.")
        evaluation_features_file = os.path.join(evaluation_data_folder, 'features.tfrecord')
        evaluation_labels_file = os.path.join(evaluation_data_folder, 'labels.tfrecord')
        result = classifier.evaluate(input_fn=lambda: input_fn(evaluation_features_file, evaluation_labels_file, epochs=1, batch_size=50, buffer_size=0))
        logging.info("Accuracy on evaluation set: %.3f", result['accuracy'])


if __name__ == '__main__':
    run()
