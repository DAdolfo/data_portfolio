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

The documentation for this project will be written in a tutorial kind of way, assuming some basic knowledge, because teaching is not only the best way to learn, it's the best way to notice where you missed something. I'll add a highglight when I mention a problem I faced. 

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

Keep in mind, ==the name resources will take in AWS go inside the brackets when you declare them, the name outside the brackets is the one you'll see in your infrastructure files and outputs while using Terraform==.

#### S3 Bucket
This one is as simple as consulting the registry and choosing a bucket name, which I'd recommend testing before hand in the AWS console because ==if it already exists, its creation will fail==. Well at that point you might as well create it in the UI right?

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
4. ==Set some sleep times between commands that when testing in your local machine take time, as not setting it might lead to nothing working==. _I realized this because I thought of logging._