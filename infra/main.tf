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

resource "aws_iam_role" "ec2_role" {
  name = "airflow-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "s3_access" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect : "Allow",
        Action : [
          "s3:GetObject",    
          "s3:GetObjectVersion", 
          "s3:ListBucket",   
          "s3:PutObject",    
          "s3:DeleteObject"  
        ],
        Resource : [
          "arn:aws:s3:::data-bucket-jaguilar-9",
          "arn:aws:s3:::data-bucket-jaguilar-9/*"     
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_instance_profile" "airflow_profile" {
  name = "airflow-instance-profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_key_pair" "airflow_instance_key" {
    key_name = "airflow_instance_key"
    public_key = var.airflow_instance_publickey
}

resource "aws_instance" "airflow_instance" {
    ami = "ami-0ba5fd8ce786c1351"
    instance_type = "m8g.large"
    key_name = aws_key_pair.airflow_instance_key.key_name
    iam_instance_profile = aws_iam_instance_profile.airflow_profile.name
    vpc_security_group_ids = ["sg-033a2dfde67ca421b"]
    user_data = file("docker_airflow_install.sh")

    root_block_device {
        volume_size           = 20
        volume_type           = "gp3"
        delete_on_termination = true 

  }
}