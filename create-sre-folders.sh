#!/bin/bash

set -e

echo "Creating only missing SRE folders..."

# CI/CD
mkdir -p cicd/github-actions
mkdir -p cicd/argocd
mkdir -p cicd/gitops

# Observability
mkdir -p observability/prometheus
mkdir -p observability/grafana/dashboards
mkdir -p observability/alertmanager/rules
mkdir -p observability/exporters
mkdir -p observability/logging/fluent-bit
mkdir -p observability/logging/elasticsearch
mkdir -p observability/logging/kibana

# SRE Practices
mkdir -p sre/sli
mkdir -p sre/slo
mkdir -p sre/error-budget
mkdir -p sre/alerting
mkdir -p sre/runbooks
mkdir -p sre/incident-management
mkdir -p sre/rca

# Testing
mkdir -p testing/load-testing/k6
mkdir -p testing/load-testing/locust
mkdir -p testing/failure-testing
mkdir -p testing/latency
mkdir -p testing/error-injection

# Networking
mkdir -p networking/route53
mkdir -p networking/alb
mkdir -p networking/security-groups
mkdir -p networking/troubleshooting

# Documentation
mkdir -p docs/architecture



find . -maxdepth 3 -type d | sort
