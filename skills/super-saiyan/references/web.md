# Super Saiyan: Web Reference

Visual excellence for web interfaces using React, Vue, Tailwind, Framer Motion.

## Animation (Framer Motion)
```tsx
import { motion } from "framer-motion";

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ duration: 0.3, ease: "easeOut" }}
>
  Content
</motion.div>
```

## Timing
- Instant: <100ms (micro-interactions)
- Fast: 100-200ms (hovers)
- Normal: 200-300ms (transitions)
- Slow: 300-500ms (emphasis)

## Tailwind Patterns
```tsx
// Card with hover
<div className="bg-white rounded-lg shadow-md p-6 
  hover:shadow-lg transition-shadow duration-200">

// Button
<button className="bg-blue-500 hover:bg-blue-600 text-white 
  px-4 py-2 rounded-md transition-colors duration-150">

// Loading skeleton
<div className="animate-pulse bg-gray-200 rounded h-4 w-32">
```

## State Indicators
```tsx
// Success
<span className="text-green-500">✓</span>

// Error  
<span className="text-red-500">✗</span>

// Loading
<div className="animate-spin h-5 w-5 border-2 border-blue-500 
  border-t-transparent rounded-full">
```

## Accessibility
- Contrast: 4.5:1 text, 3:1 UI
- Focus visible: `focus:ring-2 focus:ring-blue-500`
- Motion: `motion-reduce:transition-none`
- Keyboard: all interactive elements focusable

## Checklist
- [ ] 60fps animations
- [ ] Loading/error/success states
- [ ] Keyboard navigation
- [ ] WCAG AA contrast
- [ ] Reduced motion support
- [ ] Mobile responsive
