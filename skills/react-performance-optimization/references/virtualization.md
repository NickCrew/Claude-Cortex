# Virtualization for Large Lists

## react-window Basics

**Render only visible items to handle thousands of rows:**
```jsx
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style} className="list-item">
      <h4>{items[index].title}</h4>
      <p>{items[index].description}</p>
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

## Variable Size Lists

```jsx
import { VariableSizeList } from 'react-window';

function DynamicList({ items }) {
  const getItemSize = (index) => {
    return items[index].type === 'header' ? 60 : 40;
  };

  return (
    <VariableSizeList
      height={600}
      itemCount={items.length}
      itemSize={getItemSize}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>{items[index].content}</div>
      )}
    </VariableSizeList>
  );
}
```

## Performance Impact

**Traditional list with 10,000 items:**
- DOM nodes: 10,000
- Memory usage: High
- Scroll performance: Poor

**Virtualized list:**
- DOM nodes: ~20 (only visible + buffer)
- Memory usage: Low
- Scroll performance: Smooth 60fps
- Result: 500x reduction in DOM nodes

## Library Comparison

**react-window** (Recommended)
- Lightweight (7KB gzipped)
- Simple API
- Excellent performance
- Good for most use cases

**react-virtualized**
- Feature-rich (27KB gzipped)
- Advanced components (Grid, Masonry, Table)
- More configuration options
- Better for complex layouts

**@tanstack/react-virtual**
- Modern, headless virtualization
- Framework agnostic core
- Maximum flexibility
- Better for custom implementations

## List Keys Optimization

**Proper keys prevent unnecessary re-renders:**
```jsx
// BAD: Index as key (breaks when reordering/filtering)
{items.map((item, index) => (
  <Item key={index} data={item} />
))}

// BAD: Random keys (forces complete re-render every time)
{items.map(item => (
  <Item key={Math.random()} data={item} />
))}

// GOOD: Stable unique identifier
{items.map(item => (
  <Item key={item.id} data={item} />
))}

// GOOD: Composite key when no unique ID exists
{items.map(item => (
  <Item key={`${item.userId}-${item.timestamp}`} data={item} />
))}
```

**Why keys matter:**
- React uses keys to track element identity
- Stable keys enable efficient diffing and reconciliation
- Index keys break when list order changes
- Missing keys force React to destroy/recreate components
