# Kafka Consumer Lag Runbook

## Overview
Consumer lag occurs when a Kafka consumer group falls behind the rate of message production.

## Symptoms
- Consumer lag metric exceeds threshold (default: 10,000 messages)
- Downstream service latency increases
- Dead letter queue (DLQ) starts filling up

## Diagnosis Steps
1. Check consumer group lag: `kafka-consumer-groups.sh --bootstrap-server <broker> --describe --group <group-id>`
2. Identify the partition with the highest lag.
3. Check consumer pod logs for exceptions or slow processing.
4. Verify broker CPU and disk I/O metrics in Grafana.

## Remediation
### Option A – Scale consumers
- Increase the number of consumer replicas to match partition count.
- Command: `kubectl scale deployment <consumer-deployment> --replicas=<n>`

### Option B – Reset offsets (data loss risk – get approval first)
- `kafka-consumer-groups.sh --bootstrap-server <broker> --group <group-id> --topic <topic> --reset-offsets --to-latest --execute`

## Rollback
- Scale consumers back to original count.
- Monitor lag metric for 10 minutes post-change.

## Escalation
Page the Platform Engineering on-call if lag does not reduce within 15 minutes.
