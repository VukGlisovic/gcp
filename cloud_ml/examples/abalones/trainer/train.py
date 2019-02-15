"""
Explanation on the xgboost parameters (xgb.train) (most of it is copied from the
xgboost docstring). Note that xgb.train is a low level API to train an xgb model.
classes like xgb.XGBClassifier and xgb.XGBRegressor are wrappers (for a more
scikit-learn style approach) around xgb.train. The xgb.XGBClassifier and
xgb.XGBRegressor basically convert the input to a DMatrix and pass in the
corresponding objective function and parameters to xgb.train. In other words, you
have more flexibility with xgb.train, but perhaps a more familiar feel with the
scikit-learn versions of the models.

params (dict)
    Booster params. These are parameters that correspond to the model itself. For example
    `objective` determines the loss function to be used like reg:linear for regression
    problems, reg:logistic for classification problems with only decision, binary:logistic
    for classification problems with probability and other objective functions. But
    there's many more parameters you can set. Checkout the parameters for xgb.XGBClassifier
    for example.
dtrain (xgboost.DMatrix)
    Data to be trained. Usually is a pandas dataframe or numpy array converted to
    a DMatrix
num_boost_round (int)
    Number of boosting iterations.
evals (list of pairs (DMatrix, string))
    List of items to be evaluated during training (the test set).
obj (function)
    Customized objective function.
feval (function)
    Customized evaluation function.
maximize (bool)
    Whether to maximize feval.
early_stopping_rounds (int)
    Activates early stopping. Validation error needs to decrease at least
    every `early_stopping_rounds` round(s) to continue training.
    Requires at least one item in `evals`.
    If there's more than one, will use the last.
    Returns the model from the last iteration (not the best one).
    If early stopping occurs, the model will have three additional fields:
    ``bst.best_score``, ``bst.best_iteration`` and ``bst.best_ntree_limit``.
    (Use ``bst.best_ntree_limit`` to get the correct value if
    ``num_parallel_tree`` and/or ``num_class`` appears in the parameters)
evals_result (dict)
    This dictionary stores the evaluation results of all the items in watchlist.
    Example: with a watchlist containing
    ``[(dtest,'eval'), (dtrain,'train')]`` and
    a parameter containing ``('eval_metric': 'logloss')``,
    the **evals_result** returns
    .. code-block:: python
        {'train': {'logloss': ['0.48253', '0.35953']},
         'eval': {'logloss': ['0.480385', '0.357756']}}
verbose_eval (bool or int)
    Requires at least one item in **evals**.
    If **verbose_eval** is True then the evaluation metric on the validation set is
    printed at each boosting stage.
    If **verbose_eval** is an integer then the evaluation metric on the validation set
    is printed at every given **verbose_eval** boosting stage. The last boosting stage
    / the boosting stage found by using **early_stopping_rounds** is also printed.
    Example: with ``verbose_eval=4`` and at least one item in **evals**, an evaluation metric
    is printed every 4 boosting stages, instead of every boosting stage.
learning_rates: list or function (deprecated - use callback API instead)
    List of learning rate for each boosting round
    or a customized function that calculates eta in terms of
    current number of round and the total number of boosting round (e.g. yields
    learning rate decay)
xgb_model : file name of stored xgb model or 'Booster' instance
    Xgb model to be loaded before training (allows training continuation).
callbacks : list of callback functions
    List of callback functions that are applied at end of each iteration.
    It is possible to use predefined callbacks by using
    :ref:`Callback API <callback_api>`.
"""
import os
import logging
import argparse
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from google.cloud import storage

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('--data_path',
                    help='Path to file containing the training data.',
                    type=str,
                    default=os.path.join(os.environ['HOME'], 'gcp/cloud_ml/examples/abalones/data/abalone_data.csv'))
parser.add_argument('--model_path',
                    help='Path where to store the model. Must be a cloud storage path.',
                    type=str,
                    default='gs://[YOUR_BUCKET]/output_path')

known_args, _ = parser.parse_known_args()
data_path = known_args.data_path
model_path = known_args.model_path
logging.info("Input parameters:")
logging.info("Train data filepath: %s", data_path)
logging.info("Outputs filepath: %s", model_path)


TARGET_COLUMN = 'Rings'
COLUMNS = ['Sex', 'Length', 'Diameter', 'Height', 'Whole weight', 'Shucked weight', 'Viscera weight', 'Shell weight'] + [TARGET_COLUMN]


# reading data from local or cloud storage path
with open(data_path, 'r') as train_data:
    data = pd.read_csv(train_data, header=None, names=COLUMNS)
data = pd.get_dummies(data, columns=['Sex'], drop_first=True)

feature_data = data[data.columns.drop(TARGET_COLUMN)]
target_data = data[TARGET_COLUMN]
target_data -= 1
Xtrain, Xtest, ytrain, ytest = train_test_split(feature_data, target_data, test_size=0.2)

dtrain = xgb.DMatrix(Xtrain, label=ytrain)
dtest = xgb.DMatrix(Xtest, label=ytest)

logging.info("Starting training...")

params = {'objective': 'multi:softmax', 'num_class': 29}
bst = xgb.train(params, dtrain=dtrain, num_boost_round=20, evals=[(dtrain, 'train_set'), (dtest, 'test_set')], verbose_eval=True)

logging.info("Finished training!")

logging.info("Exporting model...")
model_name = 'xgb_abalones.bst'
bst.save_model(model_name)

# Upload the model to cloud storage
bucket_name, blob_subfolder = model_path.replace('gs://', '').split('/', 1)
bucket = storage.Client().bucket(model_path)
blob_path = os.path.join(blob_subfolder, model_name)
blob = bucket.blob(blob_path)
blob.upload_from_filename(model_name)

logging.info("Finished exporting model!")
