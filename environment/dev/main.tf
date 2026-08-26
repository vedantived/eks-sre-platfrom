module "vpc" {
  source = "../../modules/vpc"

  project_name             = var.project_name
  vpc_cidr                 = var.vpc_cidr
  public_subnet_cidrs      = var.public_subnet_cidrs
  private_app_subnet_cidrs = var.private_app_subnet_cidrs

  common_tags              = var.common_tags
}


# EKS Module 

module "eks" {
  source = "../../modules/eks"

  cluster_name = "eks-sre"
cluster_role_arn = aws_iam_role.eks_cluster_role.arn

  subnet_ids = concat(
    module.vpc.private_subnet_ids,
    module.vpc.public_subnet_ids
  )


  allowed_cidrs = [
  "0.0.0.0/0"
]

  tags = {
    Environment = "dev"
    Project     = "EKS-Sre"
  }
}

#### EKS node Group

resource "aws_eks_node_group" "this" {
  cluster_name    = module.eks.cluster_name
  node_group_name = "eks-node-group"
 node_role_arn   = aws_iam_role.eks_node_role.arn

  subnet_ids = module.vpc.private_subnet_ids

  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }

  instance_types = ["t2.large"]
  capacity_type = "ON_DEMAND"

  tags = {
    Name        = "eks-node"
    Environment = "dev"
  }
}

