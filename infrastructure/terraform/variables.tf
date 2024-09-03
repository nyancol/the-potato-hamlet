variable "resource_tags" {
  description = "Tags to set for all resources"
  type        = map(string)
  default     = {
    Name = "potato-hamlet"
  }
}

variable "aws_region" {
  type    = string
  default = "eu-west-3"
}

variable "aws_subregion" {
  type    = string
  default = "eu-west-3a"
}
