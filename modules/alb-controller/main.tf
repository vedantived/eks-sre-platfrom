
# ============================================================
# TLS CERTIFICATE FOR EKS OIDC
# ============================================================

data "tls_certificate" "eks_oidc" {

  url = var.oidc_issuer_url
}


# ============================================================
# EKS OIDC PROVIDER
# ============================================================

resource "aws_iam_openid_connect_provider" "eks" {

  url = var.oidc_issuer_url

  client_id_list = [
    "sts.amazonaws.com"
  ]

  thumbprint_list = [
    data.tls_certificate.eks_oidc.certificates[0].sha1_fingerprint
  ]

  tags = {
    Name        = "${var.cluster_name}-oidc"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# IRSA TRUST POLICY
# ============================================================

data "aws_iam_policy_document" "alb_controller_assume_role" {

  statement {

    effect = "Allow"

    actions = [
      "sts:AssumeRoleWithWebIdentity"
    ]

    principals {

      type = "Federated"

      identifiers = [
        aws_iam_openid_connect_provider.eks.arn
      ]
    }

    condition {

      test = "StringEquals"

     variable = "${replace(
  var.oidc_issuer_url,
  "https://",
  ""
)}:aud"

      values = [
        "sts.amazonaws.com"
      ]
    }

    condition {

      test = "StringEquals"

     variable = "${replace(
  var.oidc_issuer_url,
  "https://",
  ""
)}:sub"

      values = [
        "system:serviceaccount:kube-system:aws-load-balancer-controller"
      ]
    }
  }
}


# ============================================================
# IAM ROLE
# ============================================================

resource "aws_iam_role" "alb_controller" {

  name = "${var.cluster_name}-alb-controller-role"

  assume_role_policy = data.aws_iam_policy_document.alb_controller_assume_role.json

  tags = {
    Name        = "${var.cluster_name}-alb-controller-role"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# IAM POLICY
# ============================================================

resource "aws_iam_policy" "alb_controller" {

  name = "${var.cluster_name}-alb-controller-policy"

  description = "IAM permissions for AWS Load Balancer Controller"

  policy = file("${path.module}/iam-policy.json")

  tags = {
    Name        = "${var.cluster_name}-alb-controller-policy"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# ATTACH POLICY TO ROLE
# ============================================================

resource "aws_iam_role_policy_attachment" "alb_controller" {

  role = aws_iam_role.alb_controller.name

  policy_arn = aws_iam_policy.alb_controller.arn
}


# ============================================================
# AWS LOAD BALANCER CONTROLLER - HELM
# ============================================================

resource "helm_release" "aws_load_balancer_controller" {

  name = "aws-load-balancer-controller"

  repository = "https://aws.github.io/eks-charts"

  chart = "aws-load-balancer-controller"

  namespace = "kube-system"

  create_namespace = false

  wait = true

  timeout = 600

  set {
    name  = "clusterName"
    value = var.cluster_name
  }

  set {
    name  = "region"
    value = var.aws_region
  }

  set {
    name  = "vpcId"
    value = var.vpc_id
  }

  set {
    name  = "replicaCount"
    value = "2"
  }

  # ----------------------------------------------------------
  # ServiceAccount
  # ----------------------------------------------------------

  set {
    name  = "serviceAccount.create"
    value = "true"
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  # ----------------------------------------------------------
  # IRSA annotation
  # ----------------------------------------------------------

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"

    value = aws_iam_role.alb_controller.arn
  }

  depends_on = [
    aws_iam_role_policy_attachment.alb_controller
  ]
}
