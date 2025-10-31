terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "6.19.0"
    }
  }
}

#S3 where the raw data will be stored
#No ownership policy because it defaults to private
resource "aws_s3_bucket" "etl_data_bucket" { 
    bucket = "data-bucket-jaguilar-9"
    force_destroy = true

    tags = {
        Name = "data_bucket_jose"
        Environment = var.environment
    }
}

resource "aws_key_pair" "airflow_instance_key" {
    key_name = "airflow_instance_key"
    public_key = var.airflow_instance_publickey
}

resource "aws_instance" "airflow_instance" {
    ami = "ami-0ba5fd8ce786c1351"
    instance_type = "m8g.large"
    key_name = aws_key_pair.airflow_instance_key.key_name
    vpc_security_group_ids = ["sg-033a2dfde67ca421b"]
    user_data = file("docker_airflow_install.sh")

    root_block_device {
        volume_size           = 20
        volume_type           = "gp3"
        delete_on_termination = true 

  }
}