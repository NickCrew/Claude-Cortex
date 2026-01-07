# Message Brokers and Event Buses

## Message Queue (Point-to-Point)

### Use Case
Work distribution, reliable delivery, load balancing.

### Architecture
```
Producer → Queue → Consumer 1
                → Consumer 2 (competes for messages)
                → Consumer N

Characteristics:
- One message consumed by one consumer
- Load balancing across consumers
- Guaranteed delivery
- Message ordering (within partition/queue)

Examples:
- RabbitMQ queues
- AWS SQS
- Azure Service Bus queues
```

### RabbitMQ Example:
```typescript
// Producer
const queue = 'order-processing';
channel.sendToQueue(
  queue,
  Buffer.from(JSON.stringify(orderEvent)),
  { persistent: true }  // survive broker restart
);

// Consumer
channel.consume(queue, async (msg) => {
  const event = JSON.parse(msg.content.toString());

  try {
    await processOrder(event);
    channel.ack(msg);  // acknowledge success
  } catch (error) {
    channel.nack(msg, false, true);  // requeue on failure
  }
});
```

## Publish-Subscribe (Pub/Sub)

### Use Case
Broadcasting events to multiple interested services.

### Architecture
```
Publisher → Topic → Subscriber 1 (all messages)
                  → Subscriber 2 (all messages)
                  → Subscriber N (all messages)

Characteristics:
- One message received by all subscribers
- Decoupled publishers and subscribers
- Dynamic subscription
- Topic-based or content-based routing

Examples:
- Apache Kafka topics
- AWS SNS
- Google Cloud Pub/Sub
- Azure Service Bus topics
```

### Kafka Example:
```typescript
// Producer
await producer.send({
  topic: 'orders',
  messages: [
    {
      key: orderEvent.orderId,  // partition key
      value: JSON.stringify(orderEvent),
      headers: {
        'event-type': 'OrderCreated',
        'correlation-id': correlationId
      }
    }
  ]
});

// Consumer Group (load balanced)
const consumer = kafka.consumer({ groupId: 'order-analytics' });
await consumer.subscribe({ topic: 'orders' });

await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    const event = JSON.parse(message.value.toString());
    await updateAnalytics(event);
  }
});
```

## Message Broker Comparison

### RabbitMQ:
**Strengths:**
- Rich routing (exchanges, bindings)
- Message acknowledgment and requeue
- Priority queues
- Dead letter exchanges

**Best for:**
- Task distribution
- Complex routing patterns
- Guaranteed delivery
- Lower throughput needs (<100K msg/sec)

### Apache Kafka:
**Strengths:**
- High throughput (millions msg/sec)
- Event log persistence
- Replay capability
- Partition-based parallelism

**Best for:**
- Event streaming
- High-volume systems
- Event sourcing backend
- Log aggregation

### AWS SQS/SNS:
**Strengths:**
- Fully managed
- Infinite scale
- Simple integration
- Pay per use

**Best for:**
- AWS-native architectures
- Variable load
- Simple pub/sub or queuing
- Minimal ops overhead
