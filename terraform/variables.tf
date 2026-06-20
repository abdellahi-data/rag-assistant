# inputs, with defaults, so the config is reusable
variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-3"
}

variable "project_name" {
  description = "Name prefix for resources"
  type        = string
  default     = "rag-assistant"
}
