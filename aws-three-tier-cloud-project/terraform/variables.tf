variable "aws_region" {
  description = "AWS region for this learning project"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  type    = string
  default = "three-tier-demo"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "db_instance_class" {
  description = "Choose a small supported instance class for learning; check regional availability and pricing."
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  type    = string
  default = "appdb"
}

variable "db_username" {
  type      = string
  default   = "appadmin"
  sensitive = true
}

variable "allowed_http_cidr" {
  description = "Public IPv4 range allowed to reach the ALB. Prefer your own public IP /32."
  type        = string
  default     = "0.0.0.0/0"
}

variable "app_instance_type" {
  type    = string
  default = "t3.micro"
}
