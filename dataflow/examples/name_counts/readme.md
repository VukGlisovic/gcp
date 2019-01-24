# Name Count Example

This example is showing how you could create a dataflow, how you can optionally create a template from a dataflow and finally
how you can start a batch dataflow.

To start a dataflow from a template, you can use the gcloud command depicted below.
```bash
gcloud dataflow jobs run name_counts_04 \
    --gcs-location=gs://name_counts_example/dataflow/templates/name_counts \
    --max-workers=2 \
    --parameters='input_path=gs://name_counts_example/data/inputs/name_file_*,output_path_template=gs://name_counts_example/data/output_{}.txt' \
    --region=europe-west1 \
    --zone=europe-west1-c
```