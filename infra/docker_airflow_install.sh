#!/bin/bash
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1
set -euxo pipefail


set -e

#Update the machine and install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sleep 15

#Install docker-compose
sudo mkdir -p /usr/libexec/docker/cli-plugins/
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose
sudo chmod +x /usr/libexec/docker/cli-plugins/docker-compose

#Install Airflow
sudo curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.1.1/docker-compose.yaml'
sudo mkdir -p ./dags ./logs ./plugins ./config
sudo echo -e "AIRFLOW_UID=$(id -u)" > .env
sleep 15
sudo docker compose --project-name airflow up airflow-init
sleep 60
sudo docker compose --project-name airflow up -d

sudo usermod -a -G docker ec2-user