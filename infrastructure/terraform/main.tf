resource "aws_key_pair" "terraform_ec2_key" {
  key_name   = "terraform_ec2_key"
  public_key = file("~/.ssh/terraform_ec2_key.pub")
}

resource "aws_vpc" "swarm_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = var.resource_tags
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.swarm_vpc.id
  tags = var.resource_tags
}


resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.swarm_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags = var.resource_tags
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.swarm_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = var.resource_tags
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}


resource "aws_security_group" "swarm_sg" {
  name        = "swarm_sg"
  description = "Security group for Docker Swarm cluster"
  vpc_id      = aws_vpc.swarm_vpc.id
  tags = var.resource_tags

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "docker_swarm" {
  count         = 1
  ami           = "ami-04a92520784b93e73"
  instance_type = "t3.micro"
  tags          = var.resource_tags
  key_name      = aws_key_pair.terraform_ec2_key.key_name
  vpc_security_group_ids = [aws_security_group.swarm_sg.id]
  subnet_id     = aws_subnet.public.id
}

resource "aws_eip" "docker_swarm_eip" {
    vpc = true
    instance = aws_instance.docker_swarm[0].id
}

resource "local_file" "ansible_vars" {
  content = yamlencode({
    instance_public_ip = aws_eip.docker_swarm_eip.public_ip
    instance_public_dns = aws_eip.docker_swarm_eip.public_dns
  })
  filename = "${path.module}/../ansible/playbooks/tf_outputs.yml"
}
