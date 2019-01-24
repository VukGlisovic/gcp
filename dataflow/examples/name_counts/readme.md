# Name Count Example

This example is showing how you could create a dataflow, how you can optionally create a template from a dataflow and finally
how you can start a batch dataflow.

First of all, run the `create_name_data.py` to generate data to test with. Add the parameters you like to execute the script.

Next, we have to create a template of our dataflow. You can do this by executing:
```bash
python task.py \
    --project=[YOUR-PROJECT] \
    --region=europe-west1 \
    --runner=DataflowRunner \
    --setup_file=${HOME}/gcp/dataflow/examples/name_counts/setup.py \
    --temp_location=gs://[YOUR_BUCKET]/dataflow/temp \
    --staging_location=gs://[YOUR_BUCKET]/dataflow/staging \
    --template_location=gs://[YOUR_BUCKET]/dataflow/templates/name_counts \
    --max-workers=2 \
    --worker-machine-type=n1-standard-1
```
The `--max-workers` and `--worker-machine-type` parameters are set as defaults for when a dataflow is started with this template.
You can add requirements and custom packages with the following parameters: `--requirements_file=requirements.txt` and
`--extra_package=additional_package-0.1-py2-none-any.whl`. In order to create a `.whl` file, you can execute
`python setup.py bdist_wheel` with the `setup.py` of the package.

To start a dataflow from our  template, you can use the gcloud command depicted below.
```bash
gcloud dataflow jobs run name_counts \
    --gcs-location=gs://[YOUR_BUCKET]/dataflow/templates/name_counts \
    --max-workers=2 \
    --parameters='input_path=gs://[YOUR_BUCKET]/data/inputs/name_file_*,output_path_template=gs://[YOUR_BUCKET]/data/output_{}.txt' \
    --region=europe-west1 \
    --zone=europe-west1-c
```
