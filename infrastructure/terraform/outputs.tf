output "instance_ids" {
  description = "IDs of created EC2 instances"
  value       = aws_instance.docker_swarm[*].id
}

output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.swarm_vpc.id
}

output "instance_public_ip" {
  value = aws_instance.docker_swarm[*].public_ip
}
