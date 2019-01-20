# Letter Statistics Calculations

This example illustrates how to get started with a simple dataproc cluster, a 
simple pyspark script and a simple dataset.

You can execute the notebook under `notebooks/dataproc/01-letter-statistics-calculation.ipynb`.
Or you can follow this readme.

First of all make sure the data is in place, therefore, run the `data_generator.py`
with the appropriate parameters set. This will create a dataset and upload it
to a cloud storage bucket. If you want to have this data locally, simply copy it
to a local directory with a `gsutil` command.

Next, upload `calculate_letter_statistics.py` (the pyspark script) and 
`initialize_cluster.sh` (the bash script for initializing a dataproc cluster).
Execute the following command for this:
```bash
gsutil cp calculate_letter_statistics.py initialize_cluster.sh gs://[YOUR_BUCKET]/[YOUR_FOLDER]
```

Create a dataproc cluster: execute the following gcloud command (this will
create a cluster named `cluster-test`):
```bash
gcloud dataproc clusters create cluster-test \
    --initialization-actions='gs://[YOUR_BUCKET]/[YOUR_FOLDER]/initialize_cluster.sh' \
    --master-boot-disk-size=200 \
    --master-machine-type='n1-standard-1' \
    --metadata=MINICONDA_VARIANT=3,MINICONDA_VERSION=4.5.11 \
    --num-master-local-ssds=0 \
    --num-masters=1 \
    --num-worker-local-ssds=0 \
    --region='europe-west1' \
    --worker-boot-disk-size=100 \
    --worker-machine-type='n1-standard-1' \
    --zone='europe-west1-d' \
    --num-workers=2 \
    --project='[YOUR_PROJECT]'
```

Wait till the cluster has completely started up. Then finally submit your job. Script parameter are passed on after the double
hyphen:
```bash
gcloud dataproc jobs submit pyspark 'gs://[YOUR_BUCKET]/[YOUR_FOLDER]/calculate_letter_statistics.py' \
    --cluster='cluster-test' \
    --project='[YOUR_PROJECT]' \
    --region='europe-west1' \
    --async \
    -- \
    --project_id='[YOUR_PROJECT]' \
    --output_path='gs://[YOUR_BUCKET]/[YOUR_OUTPUT_PATH].csv'
```

You will be able to find the results in the `output_path` in cloud storage.
