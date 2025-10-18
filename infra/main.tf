provider "aws" {
    profile = "personal"
    region = "us-east-1" 
}

#S3 where the raw data will be stored
#No ownership policy because it defaults to private
resource "aws_s3_bucket" "data_lake" { 
    bucket = "datalake_portfolio_project_jose"
    force_destroy = true

    tags = {
        Name = "deltalake_bucket"
        Environment = var.environment
    }
}

