terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_eks_node_group" "gpu_nodes" {
  cluster_name    = var.cluster_name
  node_group_name = "gpu-inference-pool"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.subnet_ids

  instance_types = ["g5.xlarge"]

  scaling_config {
    desired_size = 1
    max_size     = 3
    min_size     = 0
  }

  labels = {
    "workload-type"           = "ai-inference"
    "nvidia.com/gpu.present"  = "true"
  }

  taint {
    key    = "nvidia.com/gpu"
    value  = "true"
    effect = "NO_SCHEDULE"
  }

  tags = {
    Environment = "production"
    Team        = "ai-infra"
    ManagedBy   = "terraform"
  }
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "node_role_arn" {
  description = "IAM role ARN for the node group"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the node group"
  type        = list(string)
}

output "node_group_name" {
  value = aws_eks_node_group.gpu_nodes.node_group_name
}

output "node_group_status" {
  value = aws_eks_node_group.gpu_nodes.status
}