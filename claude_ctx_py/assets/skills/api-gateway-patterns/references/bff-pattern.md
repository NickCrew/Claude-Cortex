# Backend for Frontend (BFF) Pattern

Client-specific API gateway layers optimized for different frontend applications.

## Concept

```
Mobile App  ──→  Mobile BFF  ──→  ┐
                                  │
Web App     ──→  Web BFF     ──→  ├──→  Microservices
                                  │
Admin Panel ──→  Admin BFF   ──→  ┘

Each BFF optimized for specific client needs
```

## Mobile BFF Example

**Mobile-Optimized Endpoint:**
```javascript
// Mobile-optimized endpoint
app.get('/mobile/dashboard', async (req, res) => {
  const userId = req.user.id

  // Parallel fetch with reduced data
  const [profile, orders, notifications] = await Promise.all([
    userService.get(userId, { fields: 'id,name,avatar' }),
    orderService.list(userId, { limit: 5, status: 'active' }),
    notificationService.count(userId, { unread: true })
  ])

  // Mobile-optimized response
  res.json({
    user: {
      name: profile.name,
      avatar: profile.avatar,
      thumbnailUrl: generateThumbnail(profile.avatar, '100x100')
    },
    activeOrders: orders.map(o => ({
      id: o.id,
      status: o.status,
      totalFormatted: formatCurrency(o.total)
    })),
    unreadNotifications: notifications.count
  })
})
```

**Mobile Optimizations:**
- Reduced payload size (minimal fields)
- Pre-formatted data (currency, dates)
- Thumbnail generation
- Limited result sets
- Aggregated counts instead of full data

## Web BFF Example

**Web-Optimized Endpoint:**
```javascript
// Web-optimized endpoint with richer data
app.get('/web/dashboard', async (req, res) => {
  const userId = req.user.id

  const [profile, orders, recommendations, analytics] = await Promise.all([
    userService.get(userId),  // Full profile
    orderService.list(userId, { limit: 20 }),  // More orders
    recommendationService.get(userId),
    analyticsService.getStats(userId)
  ])

  res.json({
    user: profile,
    orders: orders,
    recommendations: recommendations,
    analytics: {
      totalSpent: analytics.totalSpent,
      orderCount: analytics.orderCount,
      averageOrderValue: analytics.averageOrderValue
    }
  })
})
```

**Web Optimizations:**
- Full data objects
- Larger result sets
- Rich analytics
- Recommendation engines
- Full user profiles

## Benefits

- **Client-specific optimization**: Payload size, data structure tailored to client needs
- **Independent evolution**: Mobile vs web requirements evolve separately
- **Reduced client complexity**: Aggregation happens at BFF, not client
- **Better performance**: Tailored data fetching eliminates over/under-fetching
- **Team autonomy**: Mobile and web teams can evolve BFFs independently

## When to Use

- Multiple frontend applications (web, mobile, admin)
- Different data requirements per client
- Need for client-specific optimizations
- Teams organized by frontend platform
- Complex aggregation requirements
