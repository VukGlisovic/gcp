import tensorflow as tf


READ_FEATURES = {'image': tf.FixedLenFeature([], dtype=tf.string)}
READ_LABELS = {'label': tf.FixedLenFeature([], dtype=tf.int64)}


def decode_image(image):
    """Parsing logic for decoding a tensorflow record containing
    feature data. In summary it does:
    1) parse
    2) decode
    3) reshape to the image shape
    4) convert to floats
    5) divide by max float in the image

    Args:
        image (tf.Tensor):

    Returns:
        tf.Tensor
    """
    parsed_features = tf.parse_single_example(serialized=image, features=READ_FEATURES)['image']
    decoded_image = tf.decode_raw(parsed_features, tf.uint8)
    decoded_image = tf.reshape(decoded_image, shape=(28, 28), name='reshape_to_28x28')
    decoded_image = tf.cast(decoded_image, tf.float32)
    decoded_image = decoded_image / 255.0
    return decoded_image


def decode_label(label):
    """Parses the label from a tensorflow example.

    Args:
        label (tf.Tensor):

    Returns:
        tf.Tensor
    """
    parsed_label = tf.parse_single_example(serialized=label, features=READ_LABELS)['label']
    return parsed_label


def input_fn(features_file, labels_file, epochs=1, batch_size=32, buffer_size=50):
    """Creates a dataset for training and evaluating your model.

    Args:
        features_file (str):
        labels_file (str):
        epochs (int):
        batch_size (int):
        buffer_size (int):

    Returns:
        tensorflow.python.data.ops.dataset_ops.RepeatDataset
    """
    # create the features Dataset
    features_dataset = tf.data.TFRecordDataset(features_file)
    features_dataset = features_dataset.map(decode_image)
    # create the labels Dataset
    labels_dataset = tf.data.TFRecordDataset(labels_file)
    labels_dataset = labels_dataset.map(decode_label)
    # zip the features and the labels dataset into one dataset
    dataset = tf.data.Dataset.zip((features_dataset, labels_dataset))
    dataset = dataset.shuffle(buffer_size)
    dataset = dataset.batch(batch_size)
    dataset = dataset.repeat(epochs)
    return dataset.make_one_shot_iterator().get_next()


def model_fn(features, labels, mode, params=None):
    """Model for the mnist dataset; multiple convolutional layers with
    pooling layers and dense layers at the end. There's 10 possible classes
    to predict; digits 0, 1, ..., 9.

    Args:
        features (list): array with dimension (None, 28, 28)
        labels (list): 1-dimensional array with dimension
        mode (str): whether to predict, train or evaluate
        params (dict): additional parameters to be used in the model

    Returns:
        tf.estimator.EstimatorSpec
    """
    conv1 = tf.layers.Conv2D(filters=16, kernel_size=(5, 5), strides=(1, 1), name='conv1')(features)
    max_pool1 = tf.layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='maxpool1')(conv1)
    conv2 = tf.layers.Conv2D(filters=16, kernel_size=(5, 5), strides=(1, 1), name='conv2')(max_pool1)
    max_pool2 = tf.layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='maxpool2')(conv2)
    flattened = tf.layers.Flatten(name='flatten')(max_pool2)
    dense1 = tf.layers.Dense(units=256, activation='relu', name='dense1')(flattened)
    dropout1 = tf.layers.Dropout(rate=0.5)(dense1)
    dense2 = tf.layers.Dense(units=128, activation='relu', name='dense2')(dropout1)
    probabilities = tf.layers.Dense(units=10, activation='softmax', name='softmax')(dense2)
    prediction = tf.argmax(probabilities, axis=1, name='argmax')

    if mode == tf.estimator.ModeKeys.PREDICT:
        prediction_results = dict(classes=prediction, probabilities=probabilities)
        return tf.estimator.EstimatorSpec(mode, prediction_results)

    loss = tf.losses.sparse_softmax_cross_entropy(labels, probabilities)
    accuracy = tf.metrics.accuracy(labels, prediction, name='accuracy')

    if mode == tf.estimator.ModeKeys.TRAIN:
        # Create the optimizer
        learning_rate = params.get('learning_rate') or 0.0001
        optimizer = tf.train.AdamOptimizer()
        train_op = optimizer.minimize(loss, global_step=tf.train.get_or_create_global_step())

        # Name tensors to be logged with LoggingTensorHook.
        tf.identity(learning_rate, 'learning_rate')
        tf.identity(loss, 'cross_entropy')
        tf.identity(accuracy[1], name='train_accuracy')
        return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

    if mode == tf.estimator.ModeKeys.EVAL:
        # Create metrics for evaluation
        eval_metrics_ops = {'accuracy': accuracy}
        return tf.estimator.EstimatorSpec(mode, prediction, loss, eval_metric_ops=eval_metrics_ops)
