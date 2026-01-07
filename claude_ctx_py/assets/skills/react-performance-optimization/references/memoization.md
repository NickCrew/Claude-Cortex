# Memoization Patterns

## React.memo for Component Memoization

**Prevent unnecessary re-renders of functional components:**
```jsx
import React, { memo } from 'react';

const ExpensiveComponent = memo(({ data, onAction }) => {
  console.log('Rendering ExpensiveComponent');

  return (
    <div>
      <h3>{data.title}</h3>
      <p>{data.description}</p>
      <button onClick={onAction}>Action</button>
    </div>
  );
});

// Custom comparison for complex props
const UserCard = memo(
  ({ user, settings }) => (
    <div>
      <h2>{user.name}</h2>
      <span>{user.email}</span>
    </div>
  ),
  (prevProps, nextProps) => {
    // Return true if props are equal (skip render)
    return prevProps.user.id === nextProps.user.id &&
           prevProps.settings.theme === nextProps.settings.theme;
  }
);
```

**When to use:**
- Component renders with same props frequently
- Expensive rendering logic (complex JSX, heavy computations)
- Child components in frequently updating parent
- List items with stable props

**When NOT to use:**
- Props change on every render (comparison overhead)
- Simple, fast-rendering components (unnecessary optimization)

## useMemo for Expensive Computations

**Cache expensive calculation results:**
```jsx
import { useMemo } from 'react';

function DataAnalyzer({ items, filters }) {
  // Recalculates only when items or filters change
  const filteredAndSorted = useMemo(() => {
    console.log('Computing filtered data');

    return items
      .filter(item => filters.categories.includes(item.category))
      .filter(item => item.price >= filters.minPrice)
      .sort((a, b) => b.score - a.score);
  }, [items, filters]);

  const statistics = useMemo(() => {
    return {
      total: filteredAndSorted.length,
      average: filteredAndSorted.reduce((sum, item) => sum + item.price, 0) /
               filteredAndSorted.length,
      maxPrice: Math.max(...filteredAndSorted.map(item => item.price))
    };
  }, [filteredAndSorted]);

  return (
    <div>
      <p>Total items: {statistics.total}</p>
      <p>Average price: ${statistics.average.toFixed(2)}</p>
    </div>
  );
}
```

**Use cases:**
- Expensive array operations (filter, map, sort, reduce)
- Complex mathematical calculations
- Data transformations and aggregations
- Creating derived data structures

**Performance impact:**
- Without useMemo: Computation runs every render
- With useMemo: Computation runs only when dependencies change

## useCallback for Stable Function References

**Prevent child re-renders caused by function reference changes:**
```jsx
import { useState, useCallback, memo } from 'react';

const ListItem = memo(({ item, onDelete, onEdit }) => {
  console.log('Rendering ListItem:', item.id);
  return (
    <div>
      <span>{item.name}</span>
      <button onClick={() => onEdit(item.id)}>Edit</button>
      <button onClick={() => onDelete(item.id)}>Delete</button>
    </div>
  );
});

function ItemList({ items }) {
  const [selectedId, setSelectedId] = useState(null);

  // Stable function reference across renders
  const handleDelete = useCallback((id) => {
    console.log('Deleting:', id);
    // API call to delete
  }, []); // No dependencies = never recreated

  const handleEdit = useCallback((id) => {
    setSelectedId(id);
    // Open edit modal
  }, [setSelectedId]); // Recreated only if setSelectedId changes

  return (
    <div>
      {items.map(item => (
        <ListItem
          key={item.id}
          item={item}
          onDelete={handleDelete}
          onEdit={handleEdit}
        />
      ))}
    </div>
  );
}
```

**Critical rule:**
- Use `useCallback` when passing functions to memoized child components
- Without it, new function reference on every render defeats memo optimization
