import os
import logging
import argparse
import pandas as pd
import xgboost as xgb

logging.basicConfig(level=logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument('--data_path',
                    help='Path to file containing the training data.',
                    type=str,
                    default=os.path.join(os.environ['HOME'], 'gcp/cloud_ml/examples/abalones/data/abalone_data.csv'))
parser.add_argument('--model_path',
                    help='Path where to store the model.',
                    type=str,
                    default=os.path.join(os.environ['HOME'], 'gcp/cloud_ml/examples/abalones/outputs/xgb_abalones.bst'))

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

Xtrain = data[data.columns.drop(TARGET_COLUMN)]
ytrain = data[TARGET_COLUMN]

dtrain = xgb.DMatrix(Xtrain, ytrain)

logging.info("Starting training...")

params = {'objective': 'reg:linear'}
bst = xgb.train(params, dtrain, num_boost_round=20)

logging.info("Finished training!")

bst.save_model(model_path)
