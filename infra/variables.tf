variable "environment" {
    description = "This resource is part of the portfolio environment"
    type = string
    default = "portfolio"
}

variable "aws_access_key" {
    description = "Access key to deploy resources"
    type = string
    sensitive = true
}

variable "aws_secret_access_key" {
    description = "Secret Access key to deploy resources"
    type = string
    sensitive = true
}

variable "airflow_instance_publickey" {
    description = "Public ssh key to connect to the EC2 instance"
    type = string
    sensitive = true
}