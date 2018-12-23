from __future__ import print_function
import os
import logging
import tensorflow as tf

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


def create_example(image, label):
    feature = {'image': _bytes_feature(image),
               'label': _int64_feature(label)}
    features = tf.train.Features(feature=feature)
    return tf.train.Example(features=features)


def write_tf_records(feature_data, label_data, output_path='train/data.tfrecord'):
    assert len(feature_data) == len(label_data), "feature_data must have same length as label_data"
    with tf.python_io.TFRecordWriter(output_path) as writer:
        for i in range(len(feature_data)):
            example = create_example(feature_data[i], label_data[i])
            writer.write(example.SerializeToString())


def read_example_for_verification():
    # Read and print data:
    sess = tf.InteractiveSession()

    # Read TFRecord file
    reader = tf.TFRecordReader()
    filename_queue = tf.train.string_input_producer(['test/data.tfrecord'])

    _, serialized_example = reader.read(filename_queue)

    # Define features
    # Tensorflow does not allow to decode with dtype=tf.uint8, therefore use tf.int64
    read_features = {
        'image': tf.FixedLenFeature([], dtype=tf.string),
        'label': tf.FixedLenFeature([], dtype=tf.int64)
    }

    # Extract features from serialized data
    read_data = tf.parse_single_example(serialized=serialized_example,
                                        features=read_features)

    # Many tf.train functions use tf.train.QueueRunner,
    # so we need to start it before we read
    tf.train.start_queue_runners(sess)

    # Print features
    image = tf.decode_raw(read_data['image'], tf.uint8)
    label = read_data['label']
    # make sure to evaluate both tensors at the same time. Otherwise one of the two will go to their next value
    for i in xrange(3):
        print("Visualizing number.")
        vis_image, vis_label = sess.run([image, label])
        # Visualize the number
        for row in vis_image.reshape((28, 28)):
            print(" ".join(list(map(lambda v: 'X' if v else '_', row))))
        print(vis_label)
        print('')


def main():
    logging.info("Downloading mnist data.")
    (Xtrain, ytrain), (Xtest, ytest) = tf.keras.datasets.mnist.load_data()

    logging.info("Storing training data.")
    if not os.path.exists('train'):
        os.mkdir('train')
    write_tf_records(Xtrain, ytrain, 'train/data.tfrecord')

    logging.info("Storing testing data.")
    if not os.path.exists('test'):
        os.mkdir('test')
    write_tf_records(Xtest, ytest, 'test/data.tfrecord')

    logging.info("Verifying stored data.")
    read_example_for_verification()


if __name__ == '__main__':
    main()
