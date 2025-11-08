# José's Portfolio Project
## Customer Analytics Platform

This project will consists of X different parts, to explore how different parts of the data cycle work. Although there are multiple tools to execute it, I chose the ones that seem to be the most common to work with. The parts and the implemented tools are the following:

1. Infrastructure creation:
    - Infrastructure as Code: Terraform 
2. Ingestion Pipeline:
    - Orchestration: Airflow
    - Transformations and Cleanup: Spark
    - Environment Control: Docker Containers
3. Warehouse:
    - Service: Snowflake
    - Loading: dbt
4. Dashboards:
    - Snowsight
5. ML Modeling:
    - Tbd, gotta learn about it
    - Tbd, gotta learn more about it

The documentation for this project will be written in a tutorial kind of way, assuming some basic knowledge, because teaching is not only the best way to learn, it's the best way to notice where you missed something. 

I had to add this line later while documenting: Registries are an amazing and beautiful thing.

### Terraform 

I found that the best way to manage resources with Terraform is to have at least 3 files, I have four but three is enough:
- `main.tf` 
- `variables.tf`
- `terraform.tfvars` (For secret variables)
- `providers.tf` (Keeps things clean, not a must)

Until now we will need two resources: 
1. An S3 bucket
2. An EC2 instance to run the computation and orchestration

**Why an EC2 instance you ask? _That's an amazing question!_**

If my intentions are to run Docker containers for every task that will come our way, why do it with EC2? Isn't that complicating things for myself?
 **Yes, and that's the whole point.**

> I want to learn how to build this things from the most basic way (I might be missing something harderd but nevermind this is hard enough) so I am able to both use, build and troubleshoot processes that depend on self managed services or something a bit more posh as EKS.
         - _José before he knew what he got himself into, 2025_

So, let's begin:

Keep in mind, the name resources will take in AWS go inside the brackets when you declare them, the name outside the brackets is the one you'll see in your infrastructure files and outputs while using Terraform.

#### S3 Bucket
This one is as simple as consulting the registry and choosing a bucket name, which I'd recommend testing before hand in the AWS console because if it already exists, its creation will fail. Well at that point you might as well create it in the UI right?

#### EC2 Instance
To have a working EC2 instance that can read from S3, we need to:
1. Create an IAM role.
2. Attach a policy to said role, this policy is the set of actions the whatever resource has the role can execute, and to which other resources these actions will be directed.
3. An Instance profile to attache the role to the instance. Let's say this is the 
4. A key pair so we can access it from our CLI.
5. A security group, I chose to create it in the UI as I thought I'd learn more with the structure they give it there. That's why it's not in the `main.tf`.

So then we can use all of those as arguments when creating the instance. Also, you'll have to choose two things: 
- **An instance type**, AWS offers many types, some great for certain scenarios, I chose an `m8g.large` because it had enough memory to not get an OOM error as I did when testing locally and its price.
- **An AMI**, this is the OS that the instance will have, I chose Amazon Linux 2023 because I'm familiar with the commands and due to the great amount of help you can find about it online.

#### The Script that Gets Airflow Running

As you may have seen, there is an argument called `user_data` in the EC2 instance declaration. This, in my case, is a bash script that will be run once the instance is up and running.

If I learned anything during my time building this project is that you should always log things, it saves time finding out what's wrong.
Thus we have `exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1`.

I'm not going to go through what every command does as I'm not applying for a junior position but I will mention the details that I had to keep in mind:
1. First, test which commands come with the OS you chose, in my case I had to get both `docker` and `git`, and I'm pretty sure the other Dockerfile used for ingestion didn't have `curl`.
2. Do your research so that the versions you're using are compatible.
3. If you're running Airflow on Docker, and plan to use the `DockerOperator` you need to mount the sock in the volumes. Also consider this is not a really security-friendly practice.
4. Set some sleep times between commands that when testing in your local machine take time, as not setting it might lead to nothing working. _I realized this because I thought of logging._

### DAGs

#### Where it all starts:

Now on Airflow 3.0+ the dag declaration is done via `@dag` while tasks can be declared via `@task`, when specific operators are used, this isn't necessary. 

I chose to have it run 10 minutes after midnight so there is time to deliver the batch of events, which will be searched for three times every 60 seconds in each retry, each delayed by 30 minutes. To avoid having the sensor take a slot in our Airflow instance, we set it to `mode="reschedule"`.

Second, I decided to have a separate environment to run the ingestion to keep our orchestration environment nice and pristine. Using a `DockerOperator` requires Docker's sock to be mounted on the Airflow instance. Also, we won't need it anymore after the run is done so it will `auto_remove` after it's finished.


### Ingestion Pipeline

First and foremost, create logs. Thus I imported the `logging` library. This facilitated finding out where processes crashed or things went sideways while building the pipeline.

Now we start with Spark, you wouldn't believe how surprised I was when having tested the whole thing in my local machine wasn't enough and I was made aware by errors in the Airflow UI that I needed hadoop if I wanted to be able to read from S3.

This is how the config that you see in the session came to be, determining that `s3a` should be used to consult S3, that the role to be used should be the one from the instance and making sure that the connection is secure.

Of course, beforehand I used SQL and Spark to explore the data that we'll be working with and that's how I came up with the schema for the files to ingest.

I like to record the amount of records entering and exiting the pipeline so we get a good view of how much data we might be losing due to null values or malformed fields. That's why the logger gets a count of records coming in (`events.count()`) and going out. 

Afterwards, I find it important to log how many records have null values and in which columns they have them. In this project's case I didn't find nulls in any other column than `user_id` so I decided to simplify the process to only take that possibility into account.

The cleanup creates fake_ids for the records that don't contain them because downstream we will need the biggest, and thus most representative, amount of data for how our customer behave to train an ML model.

To decide how many fake_ids should be inputted into a day's batch, I used the average number of sessions records with user_ids presented. In the query you can see there, we are not taking the most out of Spark as there is no partition for the dataset, which regrettably causes a lot of memory usage (this is warned by Spark itself in the logs), I thought to leave it there as an example of what could go wrong and would need troubleshooting down the road.

:white_check_mark: One possible solution for that is to create a column that extracts the hour out of the `created_at` column and partition by that.

If the format given to the fake_ids becomes an obstacle when training the ML model, we can always come back and fix it so it fits the needs better.

After that, around line 90, I mention persist which is a command that keeps the dataset in memory, I find this using to not consult the data source more than once when we have the adequate resources and the source is of great size.

After inserting the rows with their brand new fake_ids into the final dataset, we check for malformed values in different columns ensuring we have only standardized data, the ones where we have control of what the input should be anyways.

Finally when writting data down, in case a partial write was done, we set `mode = "overwrite"`.

We have it! The data that will be uploaded to our data warehouse to continue its journey into insights.

### Dockerfile

This is where things got interesting. So, what the Docker Operator in the DAG does is to create a container based on this file that runs the script that cleans the incoming data.

First, I created the script for the pipeline in my local machine. Which ran on Spark 4.0.1 and Python 3.11.3, including the group of libraries you can see in the `pipeline_requirements.txt` file, where you can see we are using Pyspark as our API to Spark.

We must install `curl` and `wget` among other commands to be able to run the file's commands. To run Spark we need the Java JDK, to read from S3 we need hadoop and the aws-java-sdk. All of these should have compatible versions.

As you can see below I changed the Spark version because 4.0.1 wasn't playing along with Hadoop, some timeout settings in Hadoop were set as strings `60s` while Spark 4.0.1 expects an int `60000` of miliseconds. After some research, Spark 3.5.0 was the one that would run smoothly with what our goal is, and thus that and Pyspark were changed to that version.

Here are the versions used in the Dockerimage:
- Spark 3.5.0
- Pyspark 3.5.0
- Java's Open JDK 17
- Hadoop 3.3.4
- AWS Java SDK bundle 1.12.367
- Python 3.11

For Spark to run we need the environment variables properly assigned, be careful as the difference between running the Java JDK on Linux and macOS (Intel based) when assigning the environment variable is just 2 letters.

- **Linux:** `JAVA_HOME="path/java-17-openjdk-arm64"`
- **macOS:** `JAVA_HOME="path/java-17-openjdk-amd64"`

This can be an issue that's hard to catch if you don't pay proper attention, and knowing it can save a lot of time.

Finally, we copy the installs to make along with the pipeline script and execute it.

## Project Execution

I'll list the steps I use to run this project:

1. Once we're in the project in the terminal, we `cd infra`, so we can then `terraform plan`.
2. Check that everything looks all right, and we can `terraform apply` so then we approve by typing `yes`.
3. This should give you a CLI output of the EC2 instance's public IP address. Copy that and paste it into a browser followed by the port 8080, it should look something like this: `87.116.182.34:8080`. 

If the page isn't loading, wait a bit because it takes some time to get Airflow up and running.

4. Log in with the secure user `airflow` and password `airflow`.

5. Now that you're in the Airflow UI, trigger the s3_check_dag DAG and watch the magic happen in the Log tab :tada: 