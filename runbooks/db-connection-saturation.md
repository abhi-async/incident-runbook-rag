# Database Connection Saturation Runbook

## Overview
Connection pool exhaustion prevents services from acquiring DB connections, causing 500 errors.

## Symptoms
- Application logs show: `connection timeout`, `too many clients`
- DB connection count near `max_connections` limit
- Service health checks failing

## Diagnosis
1. Check current connections: `SELECT count(*) FROM pg_stat_activity;`
2. Identify long-running queries: `SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;`
3. Check connection pool settings in app config (e.g., PgBouncer or HikariCP).

## Remediation
### Short-term
- Kill idle connections: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '10 minutes';`
- Restart the connection pooler (PgBouncer): `systemctl restart pgbouncer`

### Long-term
- Reduce `max_pool_size` per service and introduce a shared connection pooler.
- Review query performance and add indexes for slow queries.

## Escalation
Engage the DBA on-call if connections do not drop within 5 minutes of remediation.
