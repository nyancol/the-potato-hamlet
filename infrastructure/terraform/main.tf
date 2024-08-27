# Main resource definitions
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags       = var.resource_tags
}

resource "aws_instance" "docker_swarm" {
  count         = var.instance_count
  ami           = var.ami_id
  instance_type = var.ec2_instance_type
  tags          = var.resource_tags
}

resource "aws_security_group" "swarm_sg" {
  name        = "swarm_sg"
  description = "Security group for Docker Swarm cluster"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 2377
    to_port     = 2377
    protocol    = "tcp"
    self        = true
  }

  ingress {
    from_port   = 7946
    to_port     = 7946
    protocol    = "tcp"
    self        = true
  }

  ingress {
    from_port   = 7946
    to_port     = 7946
    protocol    = "udp"
    self        = true
  }

  ingress {
    from_port   = 4789
    to_port     = 4789
    protocol    = "udp"
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "local_file" "ansible_vars" {
  content = yamlencode({
    instance_public_ip = aws_instance.docker_swarm[0].public_ip
  })
  filename = "${path.module}/../ansible/tf_outputs.yml"
}
