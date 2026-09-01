output "oidc_provider_arn" {
  description = "EKS OIDC provider ARN"

  value = aws_iam_openid_connect_provider.eks.arn
}

output "iam_role_arn" {
  description = "IAM role ARN for AWS Load Balancer Controller"

  value = aws_iam_role.alb_controller.arn
}

output "iam_role_name" {
  description = "IAM role name"

  value = aws_iam_role.alb_controller.name
}

output "helm_release_name" {
  description = "AWS Load Balancer Controller Helm release"

  value = helm_release.aws_load_balancer_controller.name
}
