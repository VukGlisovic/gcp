from __future__ import print_function
import os
import logging
import tensorflow as tf
from cloud_ml.mnist.trainer import model

logging.basicConfig(level=logging.INFO)


def _int64_feature(value):
    """value should be a singleton.

    Actually, the dtype coming in here should be uint8.
    """
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _bytes_feature(value):
    """value is a 2D numpy array with the image data.

    Actually, the dtype coming in here should be uint8.
    """
    raw_indicator = value.tostring()
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[raw_indicator]))


# def _float_feature(value):
#     """value should be a singleton.
#     """
#     return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))


def create_features_example(image):
    """Creates a tensorflow Example out of feature data. Which
    is basically converting the image to a tensorflow record.

    Args:
        image (np.array):

    Returns:
        tf.train.Example
    """
    feature = {'image': _bytes_feature(image)}
    features = tf.train.Features(feature=feature)
    return tf.train.Example(features=features)


def create_label_example(label):
    """Creates a tensorflow Example out of label data. Which
    is basically converting the label to a tensorflow record.

    Args:
        label (int):

    Returns:
        tf.train.Example
    """
    feature = {'label': _int64_feature(label)}
    features = tf.train.Features(feature=feature)
    return tf.train.Example(features=features)


def write_tf_records(feature_data, label_data, output_dir='train/'):
    """Creates two files; a features and a labels tensorflow
    record file.

    Args:
        feature_data (np.array): 3D numpy array
        label_data (np.array): 1D numpy array
        output_dir (str):

    Returns:
        None
    """
    assert len(feature_data) == len(label_data), "feature_data must have same length as label_data"
    logging.info("Storing images.")
    features_filepath = os.path.join(output_dir, 'features.tfrecord')
    with tf.python_io.TFRecordWriter(features_filepath) as writer:
        for i in range(len(feature_data)):
            example = create_features_example(feature_data[i])
            writer.write(example.SerializeToString())
    logging.info("Storing labels.")
    labels_filepath = os.path.join(output_dir, 'labels.tfrecord')
    with tf.python_io.TFRecordWriter(labels_filepath) as writer:
        for i in range(len(feature_data)):
            example = create_label_example(label_data[i])
            writer.write(example.SerializeToString())


def visualize_examples():
    """Simply visualizes a few examples to check the validity.
    """
    sess = tf.InteractiveSession()
    test_features_path = '../data/test/features.tfrecord'
    test_labels_path = '../data/test/labels.tfrecord'
    dataset = model.input_fn(test_features_path, test_labels_path, batch_size=1, buffer_size=1)
    dataset = dataset.make_one_shot_iterator()
    for i in xrange(3):
        image, label = sess.run(dataset.get_next())
        print("Visualizing number.")
        # Visualize the number (since it's a batch, image is a 3D array)
        for row in image[0]:
            print(" ".join(list(map(lambda v: 'X' if v else '_', row))))
        print(label[0])
        print('')


def main():
    train_filepath = '../data/train'
    test_filepath = '../data/test'

    logging.info("Downloading mnist data.")
    (Xtrain, ytrain), (Xtest, ytest) = tf.keras.datasets.mnist.load_data()

    logging.info("Storing training data.")
    if not os.path.exists(train_filepath):
        os.mkdir(train_filepath)
    write_tf_records(Xtrain, ytrain, train_filepath)

    logging.info("Storing testing data.")
    if not os.path.exists(test_filepath):
        os.mkdir(test_filepath)
    write_tf_records(Xtest, ytest, test_filepath)

    logging.info("Verifying stored data.")
    visualize_examples()


if __name__ == '__main__':
    main()
