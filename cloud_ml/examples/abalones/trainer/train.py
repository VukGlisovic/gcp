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

known_args, _ = parser.parse_known_args()
data_path = known_args.data_path
logging.info("Input parameters:")
logging.info("Train data filepath: %s", data_path)


FEATURE_COLUMNS = ['Sex', 'Length', 'Diameter', 'Height', 'Whole weight', 'Shucked weight', 'Viscera weight', 'Shell weight']
TARGET_COLUMN = 'Rings'
COLUMNS = FEATURE_COLUMNS + [TARGET_COLUMN]


# reading data from local or cloud storage path
with open(data_path, 'r') as train_data:
    data = pd.read_csv(train_data, header=None, names=COLUMNS)

Xtrain = data[FEATURE_COLUMNS]
ytrain = data[TARGET_COLUMN]


