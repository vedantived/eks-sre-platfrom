terraform {

  required_version = ">= 1.5.0"

  required_providers {

    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.17"
    }

    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.1"
    }
  }
}


provider "aws" {

  region = var.aws_region
}


# ============================================================
# EKS DATA
# ============================================================

data "aws_eks_cluster" "this" {

  name = "eks-sre"

  depends_on = [
    module.eks
  ]
}


data "aws_eks_cluster_auth" "this" {

  name = "eks-sre"

  depends_on = [
    module.eks
  ]
}


# ============================================================
# HELM PROVIDER
# ============================================================

provider "helm" {

  kubernetes {

    host = data.aws_eks_cluster.this.endpoint

    cluster_ca_certificate = base64decode(
      data.aws_eks_cluster.this.certificate_authority[0].data
    )

    token = data.aws_eks_cluster_auth.this.token
  }
}
