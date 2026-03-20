# CI/CD Pipeline Failure Runbook

## Overview
This runbook covers triage and resolution of failed CI/CD pipeline runs.

## Common Failure Types
| Failure | Likely Cause |
|--------|--------------|
| Build fails | Syntax error, missing dependency |
| Tests fail | Regression introduced in PR |
| Deploy fails | Resource quota exceeded, bad config |
| Timeout | Slow network, large artifact |

## Triage Steps
1. Open the failed pipeline run in GitHub Actions / Jenkins.
2. Identify the failing stage and review logs.
3. Check if the failure is flaky (re-run once before investigating).
4. If deploy fails, check Kubernetes events: `kubectl describe pod <pod-name> -n <namespace>`

## Remediation
- **Build failures:** Fix the code, push a new commit.
- **Test failures:** Check the test report, identify regressed test, fix or skip with a comment.
- **Deploy failures:** Check resource limits and config maps; roll back if in production.

## Escalation
If a production deploy is stuck, page the on-call TPM and SRE lead within 5 minutes.
