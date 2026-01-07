# State Management for Performance

## State Structure Optimization

**Optimize state structure to minimize re-renders:**
```jsx
import { useState, createContext, useContext } from 'react';

// BAD: Single large state object causes many re-renders
function BadApp() {
  const [state, setState] = useState({
    user: {},
    settings: {},
    data: [],
    ui: { modal: false, sidebar: true }
  });

  // Changing modal state re-renders entire tree
  const toggleModal = () => setState(prev => ({
    ...prev,
    ui: { ...prev.ui, modal: !prev.ui.modal }
  }));
}

// GOOD: Split state by update frequency
function GoodApp() {
  const [user, setUser] = useState({});
  const [settings, setSettings] = useState({});
  const [data, setData] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);

  // Only components using modalOpen re-render
}
```

## Context Splitting

**Prevent unnecessary context re-renders:**
```jsx
// BEST: Context splitting for shared state
const UserContext = createContext();
const DataContext = createContext();

function App() {
  const [user, setUser] = useState({});
  const [data, setData] = useState([]);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      <DataContext.Provider value={{ data, setData }}>
        <Dashboard />
      </DataContext.Provider>
    </UserContext.Provider>
  );
}

// Components only subscribe to needed context
function UserProfile() {
  const { user } = useContext(UserContext); // Only re-renders on user change
  return <div>{user.name}</div>;
}
```

## State Management Strategies

**Choose the right tool for the job:**

### Local State First
```jsx
// useState for component-level state
const [count, setCount] = useState(0);

// useReducer for complex state logic
const [state, dispatch] = useReducer(reducer, initialState);
```

### Context for Shared State
- Split by update frequency
- Avoid putting everything in one context
- Use memo to prevent unnecessary re-renders

### External State Managers
**Zustand** (Recommended for simplicity)
```jsx
import create from 'zustand';

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 }))
}));

function Counter() {
  const count = useStore((state) => state.count);
  const increment = useStore((state) => state.increment);
  return <button onClick={increment}>{count}</button>;
}
```

**Jotai** (Atomic state management)
```jsx
import { atom, useAtom } from 'jotai';

const countAtom = atom(0);

function Counter() {
  const [count, setCount] = useAtom(countAtom);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

**Redux Toolkit** (Complex apps)
- Use for large applications
- Time-travel debugging
- DevTools integration
- Middleware ecosystem

### Server State Libraries

**React Query** (Recommended)
```jsx
import { useQuery } from '@tanstack/react-query';

function UserProfile({ userId }) {
  const { data, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5000,
  });

  if (isLoading) return <Spinner />;
  return <div>{data.name}</div>;
}
```

**SWR** (Alternative)
```jsx
import useSWR from 'swr';

function UserProfile({ userId }) {
  const { data, error } = useSWR(`/api/user/${userId}`, fetcher);

  if (error) return <Error />;
  if (!data) return <Spinner />;
  return <div>{data.name}</div>;
}
```

## Avoiding Derived State

```jsx
// BAD: Duplicate state causes sync issues
const [items, setItems] = useState([]);
const [itemCount, setItemCount] = useState(0);

// GOOD: Derive during render
const [items, setItems] = useState([]);
const itemCount = items.length; // Always in sync

// GOOD: useMemo for expensive derivations
const expensiveValue = useMemo(() =>
  items.reduce((sum, item) => sum + item.value, 0),
  [items]
);
```
