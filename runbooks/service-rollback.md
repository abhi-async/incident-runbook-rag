# Service Rollback Runbook

## Overview
This runbook describes how to roll back a service to the previous stable version using Kubernetes.

## Prerequisites
- kubectl access to the production cluster
- Knowledge of the last stable image tag (check CI/CD pipeline or ECR)

## Rollback Steps
1. Identify the current deployment: `kubectl get deployment <service-name> -n production`
2. View rollout history: `kubectl rollout history deployment/<service-name> -n production`
3. Roll back to the previous revision: `kubectl rollout undo deployment/<service-name> -n production`
4. Confirm pods are healthy: `kubectl get pods -n production -l app=<service-name>`
5. Run smoke tests against the endpoint.

## Verify Success
- All pods in `Running` state with 0 restarts.
- P99 latency returns to baseline within 5 minutes.
- Error rate drops below 0.1%.

## Post-Rollback Actions
- Open a P1 incident ticket if not already done.
- Notify stakeholders via the #incidents Slack channel.
- Schedule a post-mortem within 48 hours.

## Escalation
If rollback fails, page the SRE lead immediately.
