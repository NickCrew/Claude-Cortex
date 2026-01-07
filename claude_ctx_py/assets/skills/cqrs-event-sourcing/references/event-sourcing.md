# Reference: Event Sourcing Deep Dive

Complete implementation patterns for event sourcing, including event store design, snapshots, and temporal queries.

## Event Store Design

### Event Store Schema

```sql
-- PostgreSQL example
CREATE TABLE events (
  event_id UUID PRIMARY KEY,
  stream_id VARCHAR(255) NOT NULL,      -- Aggregate ID
  stream_type VARCHAR(100) NOT NULL,    -- Aggregate type
  event_type VARCHAR(100) NOT NULL,
  event_data JSONB NOT NULL,
  event_metadata JSONB,
  event_version INTEGER NOT NULL,       -- Aggregate version
  global_position BIGSERIAL NOT NULL,   -- Global ordering
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  correlation_id UUID,
  causation_id UUID,

  CONSTRAINT unique_stream_version
    UNIQUE (stream_id, event_version)
);

-- Indexes for performance
CREATE INDEX idx_events_stream ON events(stream_id, event_version);
CREATE INDEX idx_events_global_position ON events(global_position);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_correlation ON events(correlation_id);

-- Snapshots for performance optimization
CREATE TABLE snapshots (
  snapshot_id UUID PRIMARY KEY,
  stream_id VARCHAR(255) NOT NULL,
  stream_type VARCHAR(100) NOT NULL,
  aggregate_data JSONB NOT NULL,
  version INTEGER NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT unique_stream_version_snapshot
    UNIQUE (stream_id, version)
);

CREATE INDEX idx_snapshots_stream ON snapshots(stream_id, version DESC);
```

### Event Store Implementation

```typescript
class PostgresEventStore implements EventStore {
  constructor(private readonly pool: Pool) {}

  async appendEvents(
    streamId: string,
    streamType: string,
    events: DomainEvent[],
    expectedVersion: number
  ): Promise<void> {
    const client = await this.pool.connect();

    try {
      await client.query('BEGIN');

      for (let i = 0; i < events.length; i++) {
        const event = events[i];
        const version = expectedVersion + i + 1;

        await client.query(
          `INSERT INTO events (
            event_id, stream_id, stream_type, event_type,
            event_data, event_metadata, event_version,
            timestamp, correlation_id, causation_id
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
          [
            event.eventId,
            streamId,
            streamType,
            event.eventType,
            JSON.stringify(event.data),
            JSON.stringify(event.metadata),
            version,
            event.timestamp,
            event.correlationId,
            event.causationId
          ]
        );
      }

      await client.query('COMMIT');
    } catch (error) {
      await client.query('ROLLBACK');

      // Optimistic concurrency check
      if (error.code === '23505') { // Unique constraint violation
        throw new ConcurrencyError(
          `Stream ${streamId} was modified by another process`
        );
      }

      throw error;
    } finally {
      client.release();
    }
  }

  async readEvents(
    streamId: string,
    fromVersion: number = 0
  ): Promise<DomainEvent[]> {
    const result = await this.pool.query(
      `SELECT event_id, event_type, event_data, event_metadata,
              event_version, timestamp, correlation_id, causation_id
       FROM events
       WHERE stream_id = $1 AND event_version > $2
       ORDER BY event_version ASC`,
      [streamId, fromVersion]
    );

    return result.rows.map(row => this.deserializeEvent(row));
  }

  async readAllEvents(
    fromPosition: number = 0,
    maxCount: number = 1000
  ): Promise<DomainEvent[]> {
    const result = await this.pool.query(
      `SELECT stream_id, stream_type, event_id, event_type,
              event_data, event_metadata, event_version,
              global_position, timestamp, correlation_id, causation_id
       FROM events
       WHERE global_position > $1
       ORDER BY global_position ASC
       LIMIT $2`,
      [fromPosition, maxCount]
    );

    return result.rows.map(row => this.deserializeEvent(row));
  }

  async getStreamVersion(streamId: string): Promise<number> {
    const result = await this.pool.query(
      `SELECT MAX(event_version) as version
       FROM events
       WHERE stream_id = $1`,
      [streamId]
    );

    return result.rows[0]?.version || 0;
  }

  private deserializeEvent(row: any): DomainEvent {
    return {
      eventId: row.event_id,
      streamId: row.stream_id,
      streamType: row.stream_type,
      eventType: row.event_type,
      data: row.event_data,
      metadata: row.event_metadata,
      version: row.event_version,
      globalPosition: row.global_position,
      timestamp: row.timestamp,
      correlationId: row.correlation_id,
      causationId: row.causation_id
    };
  }
}
```

## Snapshot Pattern

### Snapshot Strategy

```typescript
class SnapshotStrategy {
  // Snapshot every N events
  shouldCreateSnapshot(version: number): boolean {
    return version % 50 === 0;
  }

  async saveSnapshot(
    streamId: string,
    streamType: string,
    aggregate: AggregateRoot,
    version: number
  ): Promise<void> {
    await this.pool.query(
      `INSERT INTO snapshots (
        snapshot_id, stream_id, stream_type,
        aggregate_data, version, timestamp
      ) VALUES ($1, $2, $3, $4, $5, NOW())`,
      [
        generateId(),
        streamId,
        streamType,
        JSON.stringify(aggregate.getState()),
        version
      ]
    );
  }

  async loadSnapshot(
    streamId: string
  ): Promise<{ snapshot: any; version: number } | null> {
    const result = await this.pool.query(
      `SELECT aggregate_data, version
       FROM snapshots
       WHERE stream_id = $1
       ORDER BY version DESC
       LIMIT 1`,
      [streamId]
    );

    if (result.rows.length === 0) {
      return null;
    }

    return {
      snapshot: result.rows[0].aggregate_data,
      version: result.rows[0].version
    };
  }
}

// Repository with snapshot support
class SnapshotAwareRepository {
  async load(streamId: string): Promise<Order> {
    // Try to load from snapshot
    const snapshotData = await this.snapshotStrategy.loadSnapshot(streamId);

    let order: Order;
    let fromVersion: number;

    if (snapshotData) {
      // Reconstruct from snapshot
      order = Order.fromSnapshot(snapshotData.snapshot);
      fromVersion = snapshotData.version;
    } else {
      // Start fresh
      order = new Order();
      fromVersion = 0;
    }

    // Load events since snapshot
    const events = await this.eventStore.readEvents(streamId, fromVersion);

    // Apply remaining events
    for (const event of events) {
      order.apply(event);
    }

    return order;
  }

  async save(order: Order): Promise<void> {
    const streamId = order.getId();
    const uncommittedEvents = order.getUncommittedEvents();
    const expectedVersion = order.getVersion() - uncommittedEvents.length;

    // Append events
    await this.eventStore.appendEvents(
      streamId,
      'Order',
      uncommittedEvents,
      expectedVersion
    );

    // Check if snapshot needed
    if (this.snapshotStrategy.shouldCreateSnapshot(order.getVersion())) {
      await this.snapshotStrategy.saveSnapshot(
        streamId,
        'Order',
        order,
        order.getVersion()
      );
    }

    order.markEventsAsCommitted();
  }
}
```

## Temporal Queries

### Point-in-Time Reconstruction

```typescript
class TemporalQueryService {
  async getAggregateAtTime(
    streamId: string,
    asOfDate: Date
  ): Promise<Order> {
    // Load events up to specified time
    const events = await this.pool.query(
      `SELECT event_id, event_type, event_data, event_metadata,
              event_version, timestamp
       FROM events
       WHERE stream_id = $1 AND timestamp <= $2
       ORDER BY event_version ASC`,
      [streamId, asOfDate]
    );

    // Reconstruct aggregate
    const order = new Order();
    for (const row of events.rows) {
      const event = this.deserializeEvent(row);
      order.apply(event);
    }

    return order;
  }

  async getOrderStatusHistory(
    orderId: string
  ): Promise<OrderStatusHistoryItem[]> {
    const events = await this.eventStore.readEvents(orderId);

    const history: OrderStatusHistoryItem[] = [];
    let currentStatus = 'PENDING';

    for (const event of events) {
      switch (event.eventType) {
        case 'OrderCreated':
          history.push({
            status: 'PENDING',
            timestamp: event.timestamp,
            version: event.version
          });
          break;

        case 'OrderPaid':
          currentStatus = 'PAID';
          history.push({
            status: 'PAID',
            timestamp: event.timestamp,
            version: event.version
          });
          break;

        case 'OrderShipped':
          currentStatus = 'SHIPPED';
          history.push({
            status: 'SHIPPED',
            timestamp: event.timestamp,
            version: event.version
          });
          break;

        case 'OrderCancelled':
          currentStatus = 'CANCELLED';
          history.push({
            status: 'CANCELLED',
            timestamp: event.timestamp,
            version: event.version
          });
          break;
      }
    }

    return history;
  }

  async getAggregateAtVersion(
    streamId: string,
    version: number
  ): Promise<Order> {
    const events = await this.pool.query(
      `SELECT event_id, event_type, event_data, event_metadata,
              event_version, timestamp
       FROM events
       WHERE stream_id = $1 AND event_version <= $2
       ORDER BY event_version ASC`,
      [streamId, version]
    );

    const order = new Order();
    for (const row of events.rows) {
      const event = this.deserializeEvent(row);
      order.apply(event);
    }

    return order;
  }
}
```
