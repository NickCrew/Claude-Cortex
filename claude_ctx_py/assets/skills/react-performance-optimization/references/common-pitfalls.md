# Common Performance Pitfalls

## 1. Inline Object/Array Props

### The Problem
```jsx
// BAD: New object every render defeats memo
function Parent() {
  return <Component config={{ theme: 'dark' }} />;
}

const Component = memo(({ config }) => {
  // Re-renders every time because config is a new object
  return <div>{config.theme}</div>;
});
```

### Solutions
```jsx
// GOOD: Stable reference with useMemo
function Parent() {
  const config = useMemo(() => ({ theme: 'dark' }), []);
  return <Component config={config} />;
}

// BEST: Extract to constant if truly static
const CONFIG = { theme: 'dark' };

function Parent() {
  return <Component config={CONFIG} />;
}

// ALSO GOOD: Pass primitives directly
function Parent() {
  return <Component theme="dark" />;
}
```

## 2. Anonymous Functions in JSX

### The Problem
```jsx
// BAD: New function every render
function List({ items }) {
  return items.map(item => (
    <Item
      key={item.id}
      onClick={() => handleClick(item.id)}
    />
  ));
}
```

### Solutions
```jsx
// GOOD: useCallback with stable reference
function List({ items }) {
  const handleItemClick = useCallback((id) => {
    handleClick(id);
  }, []);

  return items.map(item => (
    <Item
      key={item.id}
      onClick={() => handleItemClick(item.id)}
    />
  ));
}

// ACCEPTABLE: For top-level handlers (not passed to memoized children)
function Form() {
  return (
    <button onClick={(e) => console.log(e.target.value)}>
      Click
    </button>
  );
}
```

## 3. Over-Memoization

### The Problem
```jsx
// BAD: Unnecessary memoization adds overhead
const SimpleComponent = memo(({ text }) => <span>{text}</span>);

const number = useMemo(() => 2 + 2, []); // Pointless

const handleClick = useCallback(() => {
  console.log('clicked');
}, []); // Only useful if passed to memoized child
```

### When to Memoize
```jsx
// GOOD: Only memoize if expensive or frequently re-rendered with same props
const ExpensiveComponent = memo(({ data }) => {
  // Complex rendering logic
  const processed = processLargeDataset(data);
  return <ComplexVisualization data={processed} />;
});

// GOOD: useMemo for actual expensive computations
const sortedData = useMemo(() => {
  return largeArray.sort((a, b) => b.score - a.score);
}, [largeArray]);

// GOOD: useCallback when passing to memoized children
const MemoizedChild = memo(ChildComponent);

function Parent() {
  const handleAction = useCallback(() => {
    // handler logic
  }, []);

  return <MemoizedChild onAction={handleAction} />;
}
```

## 4. Deriving State Unnecessarily

### The Problem
```jsx
// BAD: Duplicate state causes sync issues
function BadComponent({ items }) {
  const [itemsState, setItemsState] = useState(items);
  const [itemCount, setItemCount] = useState(items.length);

  // Easy to forget to update itemCount
  const addItem = (item) => {
    setItemsState([...itemsState, item]);
    setItemCount(itemCount + 1); // Can get out of sync
  };
}
```

### Solutions
```jsx
// GOOD: Derive during render
function GoodComponent({ items }) {
  const [itemsState, setItemsState] = useState(items);
  const itemCount = itemsState.length; // Always in sync

  const addItem = (item) => {
    setItemsState([...itemsState, item]);
  };
}

// GOOD: useMemo for expensive derivations only
function ComponentWithExpensiveCalc({ items }) {
  const statistics = useMemo(() => {
    return {
      count: items.length,
      total: items.reduce((sum, item) => sum + item.value, 0),
      average: items.reduce((sum, item) => sum + item.value, 0) / items.length
    };
  }, [items]);
}
```

## 5. Incorrect Dependencies

### The Problem
```jsx
// BAD: Missing dependencies (stale closures)
function Search() {
  const [filter, setFilter] = useState('');

  const fetchData = useCallback(() => {
    fetch(`/api/data?filter=${filter}`);
  }, []); // Missing filter dependency!
}

// BAD: Object/array dependencies (always new reference)
function DataComponent() {
  const config = { url: '/api', filter };

  useEffect(() => {
    fetchData(config);
  }, [config]); // New object every render = runs every render
}
```

### Solutions
```jsx
// GOOD: Include all dependencies
function Search() {
  const [filter, setFilter] = useState('');

  const fetchData = useCallback(() => {
    fetch(`/api/data?filter=${filter}`);
  }, [filter]); // Includes filter
}

// GOOD: Primitive dependencies
function DataComponent() {
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchData({ url: '/api', filter });
  }, [filter]); // Only primitive
}

// GOOD: Stable reference with useMemo
function DataComponent() {
  const [filter, setFilter] = useState('');
  const config = useMemo(() => ({ url: '/api', filter }), [filter]);

  useEffect(() => {
    fetchData(config);
  }, [config]);
}
```

## 6. Context Performance Issues

### The Problem
```jsx
// BAD: Single context with everything causes widespread re-renders
const AppContext = createContext();

function App() {
  const [user, setUser] = useState({});
  const [theme, setTheme] = useState('light');
  const [data, setData] = useState([]);

  return (
    <AppContext.Provider value={{ user, theme, data, setUser, setTheme, setData }}>
      <Dashboard />
    </AppContext.Provider>
  );
}

// Every component re-renders when ANY value changes
```

### Solutions
```jsx
// GOOD: Split contexts by update frequency
const UserContext = createContext();
const ThemeContext = createContext();
const DataContext = createContext();

function App() {
  const [user, setUser] = useState({});
  const [theme, setTheme] = useState('light');
  const [data, setData] = useState([]);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      <ThemeContext.Provider value={{ theme, setTheme }}>
        <DataContext.Provider value={{ data, setData }}>
          <Dashboard />
        </DataContext.Provider>
      </ThemeContext.Provider>
    </UserContext.Provider>
  );
}

// Components only re-render when their specific context changes
function UserProfile() {
  const { user } = useContext(UserContext); // Only re-renders on user change
  return <div>{user.name}</div>;
}
```

## 7. Large Component Files

### The Problem
- Difficult to optimize specific parts
- Hard to identify performance bottlenecks
- Monolithic re-renders

### Solution
```jsx
// Split into smaller, focused components
// Each can be optimized independently

// Before: One large component
function Dashboard() {
  return (
    <div>
      {/* 500 lines of JSX */}
    </div>
  );
}

// After: Focused components
function Dashboard() {
  return (
    <div>
      <Header />
      <Sidebar />
      <MainContent />
      <Footer />
    </div>
  );
}

const Header = memo(HeaderComponent);
const Sidebar = memo(SidebarComponent);
const MainContent = memo(MainContentComponent);
```

## 8. Image Loading Issues

### The Problem
```jsx
// BAD: All images load immediately
function Gallery({ images }) {
  return (
    <div>
      {images.map(img => (
        <img key={img.id} src={img.url} alt={img.alt} />
      ))}
    </div>
  );
}
```

### Solutions
```jsx
// GOOD: Native lazy loading
function Gallery({ images }) {
  return (
    <div>
      {images.map(img => (
        <img
          key={img.id}
          src={img.url}
          alt={img.alt}
          loading="lazy"
          decoding="async"
        />
      ))}
    </div>
  );
}

// BETTER: Intersection Observer for custom loading
import { useEffect, useRef, useState } from 'react';

function LazyImage({ src, alt }) {
  const [isLoaded, setIsLoaded] = useState(false);
  const imgRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsLoaded(true);
          observer.disconnect();
        }
      },
      { rootMargin: '50px' }
    );

    if (imgRef.current) observer.observe(imgRef.current);

    return () => observer.disconnect();
  }, []);

  return (
    <img
      ref={imgRef}
      src={isLoaded ? src : '/placeholder.jpg'}
      alt={alt}
    />
  );
}
```
