output "application_url" {
  description = "Open this URL after the EC2 instances pass ALB health checks."
  value       = "http://${aws_lb.app.dns_name}"
}

output "load_balancer_dns" {
  value = aws_lb.app.dns_name
}

output "rds_endpoint" {
  description = "Private database endpoint; not reachable from your laptop."
  value       = aws_db_instance.postgres.address
}

output "s3_bucket_name" {
  value = aws_s3_bucket.artifacts.bucket
}

output "vpc_id" {
  value = aws_vpc.main.id
}
