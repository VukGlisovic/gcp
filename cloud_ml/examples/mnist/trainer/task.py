import os
import logging
import argparse
from . import model as m
import tensorflow as tf

logging.basicConfig(level=logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument('--train_data_folder',
                    help='Path to folder containing the training data. This folder should have '
                         'two files: features.tfrecord and labels.tfrecord',
                    type=str,
                    default=os.path.join(os.environ['HOME'], 'gcp/cloud_ml/examples/mnist/data/train/'))
parser.add_argument('--evaluation_data_folder',
                    help='Path to folder containing the evaluation data. This folder should likewise'
                         'containt two files. If not provided, no evaluation will be done.',
                    type=str,
                    default='')
parser.add_argument('--model_dir',
                    help='Output directory for storing checkpoints and model.',
                    type=str,
                    default=os.path.join(os.environ['HOME'], 'gcp/cloud_ml/examples/mnist/outputs/'))
parser.add_argument('--nr_epochs',
                    help='Number of times to iterate over the entire dataset.',
                    type=int,
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
    classifier = tf.estimator.Estimator(model_fn=m.model_fn,
                                        model_dir=model_dir,
                                        params=params)

    logging.info("Starting training of mnist model.")
    logging.info("You can checkout tensorboard with the following command:\ntensorboard --logdir='%s'", model_dir)
    train_features_file = os.path.join(train_data_folder, 'features.tfrecord')
    train_labels_file = os.path.join(train_data_folder, 'labels.tfrecord')
    classifier.train(input_fn=lambda: m.input_fn(train_features_file, train_labels_file, epochs=nr_epochs, batch_size=32, buffer_size=50))

    if evaluation_data_folder:
        logging.info("Evaluate accuracy of the model.")
        evaluation_features_file = os.path.join(evaluation_data_folder, 'features.tfrecord')
        evaluation_labels_file = os.path.join(evaluation_data_folder, 'labels.tfrecord')
        result = classifier.evaluate(input_fn=lambda: m.input_fn(evaluation_features_file, evaluation_labels_file, epochs=1, batch_size=50, buffer_size=0))
        logging.info("Accuracy on evaluation set: %.3f", result['accuracy'])
    else:
        logging.info("No evaluation requested.")


def train_and_evaluate():
    """Run the training and evaluate using the high level API."""
    train_features_file = os.path.join(train_data_folder, 'features.tfrecord')
    train_labels_file = os.path.join(train_data_folder, 'labels.tfrecord')
    batch_size = 32
    train_input = lambda: m.input_fn(train_features_file, train_labels_file, epochs=nr_epochs, batch_size=batch_size, buffer_size=50)

    evaluation_features_file = os.path.join(evaluation_data_folder, 'features.tfrecord')
    evaluation_labels_file = os.path.join(evaluation_data_folder, 'labels.tfrecord')
    eval_input = lambda: m.input_fn(evaluation_features_file, evaluation_labels_file, epochs=1, batch_size=50, buffer_size=0)

    # Training set contains 60000 examples; this will make sure the train input function terminates at the same time with the TrainSpec
    max_steps = 60000 * nr_epochs // batch_size
    logging.info("Max training steps: %s", max_steps)
    train_spec = tf.estimator.TrainSpec(train_input, max_steps=max_steps)

    exporter = tf.estimator.FinalExporter('mnist', m.json_serving_input_fn)
    eval_spec = tf.estimator.EvalSpec(eval_input, steps=None, exporters=[exporter], name='mnist-eval', throttle_secs=0)

    train_config = tf.estimator.RunConfig(save_checkpoints_steps=500, keep_checkpoint_max=5)

    params = dict(learning_rate=learning_rate)
    classifier = tf.estimator.Estimator(model_fn=m.model_fn,
                                        model_dir=model_dir,
                                        params=params,
                                        config=train_config)

    logging.info("You can checkout tensorboard with the following command:\ntensorboard --logdir='%s'", model_dir)
    eval_result, export_results = tf.estimator.train_and_evaluate(classifier, train_spec, eval_spec)
    logging.info("Accuracy: %.3f", eval_result['accuracy'])
    logging.info("Export location: %s", export_results[-1])


if __name__ == '__main__':
    # run()
    train_and_evaluate()
