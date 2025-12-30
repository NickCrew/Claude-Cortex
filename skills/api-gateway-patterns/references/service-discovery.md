# Service Discovery Integration

Dynamic service registration and discovery for API gateways in microservices environments.

## Dynamic Service Registry

**Consul Integration Pattern:**

### Service Registration

```javascript
const consul = require('consul')({ host: 'consul.service' })

// Service registration
async function registerService() {
  await consul.agent.service.register({
    id: `user-service-${process.env.INSTANCE_ID}`,
    name: 'user-service',
    address: process.env.SERVICE_IP,
    port: process.env.SERVICE_PORT,
    check: {
      http: `http://${process.env.SERVICE_IP}:${process.env.SERVICE_PORT}/health`,
      interval: '10s',
      timeout: '5s'
    },
    tags: ['api', 'v1', 'production']
  })
}
```

### Service Discovery in Gateway

```javascript
// Service discovery in gateway
async function getServiceInstances(serviceName) {
  const result = await consul.health.service({
    service: serviceName,
    passing: true  // Only healthy instances
  })

  return result.map(entry => ({
    address: entry.Service.Address,
    port: entry.Service.Port
  }))
}
```

### Load Balancing

```javascript
// Load balancing
async function routeRequest(serviceName, request) {
  const instances = await getServiceInstances(serviceName)
  const instance = loadBalancer.pick(instances)  // Round-robin, least-conn, etc.

  return proxy.forward(request, `http://${instance.address}:${instance.port}`)
}
```

## Load Balancing Algorithms

**Round Robin:**
- Distribute requests evenly across instances
- Simple, fair distribution
- No awareness of instance load

**Least Connections:**
- Route to instance with fewest active connections
- Better for variable request durations
- Requires connection tracking

**Weighted Round Robin:**
- Distribute based on instance capacity
- Useful for heterogeneous instance sizes
- Requires weight configuration

**IP Hash:**
- Route based on client IP
- Ensures same client → same instance
- Useful for session affinity

## Health Checks

**Active Health Checks:**
- Gateway actively polls service health endpoints
- Removes unhealthy instances from rotation
- Configurable intervals and thresholds

**Passive Health Checks:**
- Monitor actual request success/failure
- Remove instances after N consecutive failures
- Re-introduce after recovery

## Benefits

- **Dynamic scaling**: Automatically discover new instances
- **High availability**: Remove unhealthy instances
- **Zero-downtime deployments**: Gradual instance replacement
- **Elastic infrastructure**: Services scale up/down transparently
