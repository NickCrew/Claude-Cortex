# Schema Design Patterns

## Pattern 1: Normalization (1NF, 2NF, 3NF, BCNF)

**Purpose**: Eliminate data redundancy and maintain consistency.

**First Normal Form (1NF):**
```sql
-- Violation: Multiple values in single column
CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  customer_name VARCHAR(100),
  products VARCHAR(500)  -- "Product1,Product2,Product3"
);

-- 1NF: Atomic values only
CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  customer_name VARCHAR(100)
);

CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  quantity INT,
  PRIMARY KEY (order_id, product_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

**Third Normal Form (3NF):**
```sql
-- Violation: Transitive dependency
CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  employee_name VARCHAR(100),
  department_id INT,
  department_name VARCHAR(100),  -- Depends on department_id
  department_budget DECIMAL(12,2)  -- Depends on department_id
);

-- 3NF: Remove transitive dependencies
CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  employee_name VARCHAR(100),
  department_id INT,
  FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE departments (
  department_id INT PRIMARY KEY,
  department_name VARCHAR(100),
  department_budget DECIMAL(12,2)
);
```

**When to Use:**
- OLTP systems with frequent writes
- Strong consistency requirements
- Complex business rules
- Data integrity critical

**Trade-offs:**
- More tables = more joins
- Can slow down read-heavy workloads
- Complex queries for reporting

## Pattern 2: Denormalization for Performance

**Purpose**: Optimize read performance by storing redundant data.

```sql
-- Normalized (requires joins)
SELECT o.order_id, o.order_date, c.customer_name, c.email
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- Denormalized (single table query)
CREATE TABLE orders_denormalized (
  order_id INT PRIMARY KEY,
  order_date DATE,
  customer_id INT,
  customer_name VARCHAR(100),  -- Redundant
  customer_email VARCHAR(100),  -- Redundant
  order_total DECIMAL(10,2)
);

-- Trade-off: Faster reads, but must update customer info in multiple places
```

**When to Use:**
- Read-heavy workloads (OLAP, analytics)
- Reporting dashboards
- Caching materialized views
- Data warehouses

**Strategies:**
- Materialized views
- Aggregate tables
- Computed columns
- ETL into data warehouse

## Pattern 3: Star Schema (Data Warehousing)

**Purpose**: Optimize analytical queries with fact and dimension tables.

```sql
-- Fact table (quantitative data)
CREATE TABLE sales_fact (
  sale_id BIGINT PRIMARY KEY,
  date_id INT,
  product_id INT,
  customer_id INT,
  store_id INT,
  quantity INT,
  revenue DECIMAL(12,2),
  cost DECIMAL(12,2),
  profit DECIMAL(12,2),
  FOREIGN KEY (date_id) REFERENCES date_dimension(date_id),
  FOREIGN KEY (product_id) REFERENCES product_dimension(product_id),
  FOREIGN KEY (customer_id) REFERENCES customer_dimension(customer_id),
  FOREIGN KEY (store_id) REFERENCES store_dimension(store_id)
);

-- Dimension tables (descriptive attributes)
CREATE TABLE date_dimension (
  date_id INT PRIMARY KEY,
  date DATE,
  year INT,
  quarter INT,
  month INT,
  day_of_week VARCHAR(10),
  is_holiday BOOLEAN
);

CREATE TABLE product_dimension (
  product_id INT PRIMARY KEY,
  product_name VARCHAR(200),
  category VARCHAR(100),
  brand VARCHAR(100),
  price DECIMAL(10,2)
);

-- Query: Total revenue by product category and quarter
SELECT
  p.category,
  d.year,
  d.quarter,
  SUM(s.revenue) as total_revenue
FROM sales_fact s
JOIN product_dimension p ON s.product_id = p.product_id
JOIN date_dimension d ON s.date_id = d.date_id
GROUP BY p.category, d.year, d.quarter;
```

**Benefits:**
- Simple queries for analysts
- Excellent query performance
- Easy to understand structure

## Pattern 4: Document Design (MongoDB)

**Purpose**: Store related data together for efficient retrieval.

**Embedding (One-to-Few):**
```javascript
// Good: Embed related data accessed together
{
  "_id": ObjectId("..."),
  "customer_name": "John Doe",
  "email": "john@example.com",
  "addresses": [
    {
      "type": "shipping",
      "street": "123 Main St",
      "city": "Boston",
      "state": "MA",
      "zip": "02101"
    },
    {
      "type": "billing",
      "street": "456 Oak Ave",
      "city": "Boston",
      "state": "MA",
      "zip": "02102"
    }
  ]
}
```

**Referencing (One-to-Many):**
```javascript
// Orders collection (parent)
{
  "_id": ObjectId("..."),
  "order_date": ISODate("2024-01-15"),
  "customer_id": ObjectId("..."),
  "item_ids": [
    ObjectId("item1"),
    ObjectId("item2"),
    ObjectId("item3")
  ]
}

// Order Items collection (children)
{
  "_id": ObjectId("item1"),
  "product_id": ObjectId("..."),
  "quantity": 2,
  "price": 29.99
}
```

**Two-Way Referencing (Many-to-Many):**
```javascript
// Products collection
{
  "_id": ObjectId("prod123"),
  "name": "Laptop",
  "category_ids": [ObjectId("cat1"), ObjectId("cat2")]
}

// Categories collection
{
  "_id": ObjectId("cat1"),
  "name": "Electronics",
  "product_ids": [ObjectId("prod123"), ObjectId("prod456")]
}
```

**Guidelines:**
- Embed data accessed together
- Reference when data is updated independently
- Avoid unbounded arrays (use pagination)
- Consider 16MB document size limit
