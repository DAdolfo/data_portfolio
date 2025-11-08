#!/bin/bash
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1
set -euxo pipefail


set -e

#Update the machine and install Docker
sudo yum update -y
sudo yum install -y docker git
sudo service docker start
sleep 15

#Install docker-compose
sudo mkdir -p /usr/libexec/docker/cli-plugins/
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose
sudo chmod +x /usr/libexec/docker/cli-plugins/docker-compose

#Install Airflow
sudo curl -LO 'https://airflow.apache.org/docs/apache-airflow/3.1.1/docker-compose.yaml'
sudo yum -y install python-pip
sudo pip install pyyaml
#Make it so it connects to docker and it doesn't load the example dags
sudo cat > modify_compose_file.py << 'EOF'
import yaml

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

with open("docker-compose.yaml", "r") as f:
        compose = yaml.safe_load(f)

        if 'volumes' in compose['x-airflow-common']:
            compose['x-airflow-common']['volumes'].append('/var/run/docker.sock:/var/run/docker.sock')

        if 'environment' in compose['x-airflow-common']:
             compose['x-airflow-common']['environment']['AIRFLOW__CORE__LOAD_EXAMPLES'] = 'false'

with open('docker-compose.yaml', 'w') as f:
    yaml.dump(compose, f, Dumper=NoAliasDumper, sort_keys=False)
EOF

sudo python3 modify_compose_file.py

#Get the dags and start Airflow
sudo mkdir -p ./dags ./logs ./plugins ./config
sudo git clone https://github.com/Dadolfo/portfolio_dags.git ./dags
sudo echo -e "AIRFLOW_UID=$(id -u)" > .env
sleep 30
sudo docker compose --project-name airflow up airflow-init
sleep 60
sudo docker compose --project-name airflow up -d

sudo usermod -a -G docker ec2-user
