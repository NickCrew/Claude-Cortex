# Observability & Cross-Cutting Concerns

The three pillars of observability: distributed tracing, centralized logging, and metrics/monitoring.

## Distributed Tracing
```
Request ID propagation:

Client → API Gateway [trace_id: abc123]
  → Service A [trace_id: abc123, span_id: 001]
    → Service B [trace_id: abc123, span_id: 002]
    → Service C [trace_id: abc123, span_id: 003]

Implementations: Jaeger, Zipkin, AWS X-Ray

Correlation:
X-Correlation-ID: abc123
X-Request-ID: req_xyz789
```

## Centralized Logging
```
Log aggregation pattern:

Services → Log Shipper → Log Aggregator → Search/Analysis

Structure logs (JSON):
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "order-service",
  "trace_id": "abc123",
  "span_id": "001",
  "message": "Order created",
  "order_id": "ord_123",
  "customer_id": "cust_456"
}

Stack: Filebeat → Logstash → Elasticsearch → Kibana
       Fluentd → Kafka → Splunk
```

## Metrics & Monitoring
```
Key Metrics (RED method):
  - Rate: requests per second
  - Errors: error rate
  - Duration: response time (p50, p95, p99)

USE method (infrastructure):
  - Utilization: CPU, memory, disk
  - Saturation: queue depth
  - Errors: error counts

Implementations: Prometheus, Grafana, DataDog
```

## Service Mesh

**Purpose**: Infrastructure layer handling service-to-service communication.

```
Features:
  - Traffic management (routing, retries, timeouts)
  - Security (mTLS, authentication)
  - Observability (metrics, tracing)
  - Resilience (circuit breaking, rate limiting)

Architecture:
  Service A ←→ Sidecar Proxy (Envoy)
                    ↕
             Control Plane (Istio/Linkerd)
                    ↕
  Service B ←→ Sidecar Proxy (Envoy)

Implementations: Istio, Linkerd, Consul Connect
```

## Observability Best Practices

### Correlation IDs

**Pattern**: Track requests across services with unique identifiers.

```
Client Request → Generate trace_id
  → Service A (trace_id, span_id: A1)
    → Service B (trace_id, span_id: B1)
    → Service C (trace_id, span_id: C1)

Headers:
X-Trace-ID: abc123xyz
X-Span-ID: service-a-span-001
X-Parent-Span-ID: gateway-span-001

Benefits:
- End-to-end request tracking
- Debug production issues
- Performance analysis
- Error correlation
```

### Structured Logging

**Pattern**: Use JSON format for machine-readable logs.

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "service": "order-service",
  "version": "1.2.3",
  "environment": "production",
  "trace_id": "abc123",
  "span_id": "span001",
  "user_id": "user456",
  "message": "Order created successfully",
  "event": "order.created",
  "order_id": "ord_789",
  "amount": 99.99,
  "duration_ms": 145,
  "http": {
    "method": "POST",
    "path": "/api/orders",
    "status": 201
  }
}

Benefits:
- Easy to parse and query
- Consistent structure
- Rich context
- Aggregation friendly
```

### Service Level Objectives (SLOs)

**Pattern**: Define and monitor service quality targets.

```
SLI (Service Level Indicator):
- Availability: 99.9% requests successful
- Latency: p95 < 200ms
- Throughput: Handle 1000 req/s

SLO (Service Level Objective):
- 99.9% availability over 30 days
- 99% of requests < 200ms (p99)
- Zero data loss

SLA (Service Level Agreement):
- Customer-facing commitment
- Financial penalties if breached
- Usually lower than internal SLO

Error Budget:
- 100% - 99.9% = 0.1% error budget
- ~43 minutes downtime per month
- When exhausted: freeze features, fix reliability
```

### Alerting Strategy

**Pattern**: Alert on symptoms, not causes.

```
✅ GOOD Alerts (user-impacting):
- Error rate > 5% for 5 minutes
- p99 latency > 1s for 5 minutes
- Availability < 99.9% over 1 hour

❌ BAD Alerts (internal metrics):
- CPU > 80% (might be normal)
- Disk > 90% (not user-facing yet)
- Memory > 70% (symptom, not problem)

Alert Levels:
- Page (critical, wake up on-call)
- Ticket (important, fix next day)
- Log (info, review weekly)

Alert Fatigue Prevention:
- Only alert on user impact
- Require action on every alert
- Group related alerts
- Auto-resolve when recovered
```

### Dashboards

**Pattern**: Visualize system health and performance.

```
Dashboard Hierarchy:

1. System Overview (executives):
   - Overall availability
   - Request rate
   - Error rate
   - Key business metrics

2. Service Dashboard (engineers):
   - Service-specific RED metrics
   - Dependency health
   - Resource utilization
   - Recent deployments

3. Detail Dashboard (debugging):
   - Per-endpoint metrics
   - Database query performance
   - Cache hit rates
   - Queue depths

Tools:
- Grafana (open source)
- DataDog (commercial)
- New Relic (commercial)
- AWS CloudWatch
```

## Observability Stack Examples

### Open Source Stack

```
Metrics:
  Prometheus (collection) → Grafana (visualization)

Logging:
  Fluentd (collection) → Elasticsearch (storage) → Kibana (visualization)

Tracing:
  Jaeger (distributed tracing)

Cost: Free (infrastructure + operational overhead)
```

### Commercial Stack

```
All-in-One:
  DataDog, New Relic, Dynatrace

Benefits:
- Integrated metrics, logs, tracing
- Advanced anomaly detection
- Automatic instrumentation
- Better support

Cost: $15-100 per host/month
```

### Hybrid Stack

```
Metrics: Prometheus (self-hosted) → Grafana Cloud (managed)
Logging: Fluentd → Splunk/Sumo Logic (managed)
Tracing: OpenTelemetry → Jaeger (self-hosted)

Benefits:
- Control over critical data
- Reduce operational burden
- Cost optimization

Cost: Mix of free and paid
```

## Security Observability

### Audit Logging

**Pattern**: Track all security-relevant events.

```json
{
  "event_type": "authentication.login",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "user123",
  "ip_address": "203.0.113.42",
  "user_agent": "Mozilla/5.0...",
  "result": "success",
  "mfa_used": true,
  "location": {
    "country": "US",
    "city": "San Francisco"
  },
  "risk_score": 0.2
}

Log these events:
- Authentication (login, logout, MFA)
- Authorization (permission checks)
- Data access (PII, financial data)
- Configuration changes
- Admin actions
```

### Anomaly Detection

**Pattern**: Detect unusual patterns automatically.

```
Examples:
- Sudden spike in 401 errors (attack?)
- Unusual geographic logins
- Abnormal data access patterns
- Unexpected service dependencies
- Traffic pattern changes

Tools:
- DataDog anomaly detection
- AWS GuardDuty
- Elastic ML (machine learning)
- Custom algorithms
```

## Tools and Technologies

### Metrics Collection
- **Prometheus**: Open source, pull-based, time-series
- **StatsD**: Push-based, simple aggregation
- **OpenTelemetry**: Unified standard
- **Cloud Native**: AWS CloudWatch, GCP Monitoring, Azure Monitor

### Logging
- **Elasticsearch**: Search and analytics engine
- **Loki**: Prometheus-inspired log aggregation
- **Splunk**: Enterprise log management
- **CloudWatch Logs**: AWS managed logging

### Distributed Tracing
- **Jaeger**: CNCF project, Uber-originated
- **Zipkin**: Twitter-originated
- **Tempo**: Grafana-integrated tracing
- **AWS X-Ray**: Managed tracing for AWS
- **OpenTelemetry**: Vendor-neutral instrumentation

### APM (Application Performance Monitoring)
- **DataDog APM**: Full-stack observability
- **New Relic**: Application monitoring
- **Dynatrace**: AI-powered monitoring
- **Elastic APM**: Open source APM

### Service Mesh
- **Istio**: Feature-rich, complex
- **Linkerd**: Lightweight, simple
- **Consul Connect**: HashiCorp service mesh
- **AWS App Mesh**: Managed service mesh

## Implementation Checklist

✓ **Metrics**:
- [ ] RED metrics per service (Rate, Errors, Duration)
- [ ] USE metrics per resource (Utilization, Saturation, Errors)
- [ ] Business metrics (orders, revenue, conversions)
- [ ] Prometheus/StatsD instrumentation
- [ ] Grafana dashboards

✓ **Logging**:
- [ ] Structured JSON logs
- [ ] Centralized log aggregation
- [ ] Correlation IDs in all logs
- [ ] Log levels properly used
- [ ] Log retention policy (30-90 days)

✓ **Tracing**:
- [ ] Distributed tracing enabled
- [ ] Trace context propagation
- [ ] Sampling strategy defined
- [ ] Trace visualization (Jaeger UI)
- [ ] Performance analysis capability

✓ **Alerting**:
- [ ] SLO-based alerts defined
- [ ] On-call rotation configured
- [ ] Alert runbooks documented
- [ ] Alert fatigue mitigated
- [ ] Escalation policy defined

✓ **Security**:
- [ ] Audit logs for sensitive operations
- [ ] Anomaly detection configured
- [ ] Security metrics tracked
- [ ] Compliance requirements met

## Further Reading

- "Distributed Systems Observability" by Cindy Sridharan
- "Site Reliability Engineering" by Google (Chapter 6: Monitoring)
- opentelemetry.io (unified observability standard)
- prometheus.io/docs/practices
- grafana.com/docs/grafana-cloud
