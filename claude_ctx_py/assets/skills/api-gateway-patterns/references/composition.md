# API Composition and Aggregation

Patterns for composing and aggregating multiple backend services into unified API responses.

## Sequential Composition

**Pattern:**
```javascript
// Gateway aggregation pattern
async function getOrderWithDetails(orderId) {
  // 1. Fetch order
  const order = await fetch(`/orders/${orderId}`)

  // 2. Fetch user (depends on order)
  const user = await fetch(`/users/${order.userId}`)

  // 3. Fetch items (depends on order)
  const items = await Promise.all(
    order.itemIds.map(id => fetch(`/items/${id}`))
  )

  // 4. Aggregate response
  return {
    order: {
      id: order.id,
      status: order.status,
      total: order.total
    },
    customer: {
      name: user.name,
      email: user.email
    },
    items: items.map(i => ({
      name: i.name,
      price: i.price
    }))
  }
}
```

**Pros:** Single client request, reduced latency
**Cons:** Gateway complexity, cascading failures
**When:** Mobile apps, high-latency networks

## Parallel Composition

**Pattern:**
```javascript
async function getDashboard(userId) {
  // Parallel fetching of independent data
  const [profile, orders, recommendations, notifications] =
    await Promise.all([
      fetch(`/users/${userId}/profile`),
      fetch(`/users/${userId}/orders`),
      fetch(`/recommendations/${userId}`),
      fetch(`/notifications/${userId}`)
    ])

  return {
    profile,
    recentOrders: orders.slice(0, 5),
    recommendations,
    unreadCount: notifications.unread_count
  }
}
```

**Benefits:**
- Optimal performance (parallel execution)
- Reduced round trips
- Better UX (single load)

## GraphQL Gateway Pattern

**Schema Stitching:**
```graphql
# Schema stitching across services
type Query {
  user(id: ID!): User @resolve(service: "user-service")
  orders(userId: ID!): [Order] @resolve(service: "order-service")
}

type User {
  id: ID!
  name: String!
  orders: [Order] @resolve(service: "order-service", field: "userId")
}
```

**Benefits:**
- Client-driven data fetching
- Eliminates over/under-fetching
- Strong typing

**When:** Complex data requirements, mobile/web apps
