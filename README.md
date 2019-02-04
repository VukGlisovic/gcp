# Google Cloud Platform

My main goal in this project, is experimenting with various products the google cloud platform
provides. I want to understand how the products work and how they can be applied to different
problems.

Note that this project is under constant development and that features can change all the time.

Based on python 3 environment:
* app_engine: scalable applications on managed serverless platform
* bigquery: highly scalable data warehouse for analytics
* bigtable: a petabyte-scale NoSQL database for large analytical and operational workloads
* cloud_ml: managed service for training on scale and for serving models in production
* cloud_storage: storage service
* dataproc: fully managed cloud service for running Apache Spark and Apache Hadoop clusters
* pubsub: processing event streams at scale for real-time stream analytics

Based on python 2 environment:
* dataflow: fulle managed service for transforming and enriching data in batch and streaming modes. 
(apache-beam is not well enough supported yet for python 3)


Every package contains a python client for executing product specific commands (starting jobs, 
create, read, update, delete operations and more). Every product also contains an examples
folder which contains usages of the product specific client. Together with the notebooks
directory, you can check out how to use the python clients and in the end how to use the google
cloud products.
