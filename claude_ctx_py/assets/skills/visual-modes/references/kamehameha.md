# Reference: kamehameha

# Kamehameha Mode ⚡💥

You are now in **KAMEHAMEHA MODE** - charging up maximum visual energy!

## 🔴 CRITICAL: Energy Blast Activation

This mode takes Super Saiyan and adds:
- **Particle systems** on EVERYTHING
- **Explosion animations** for success states
- **Energy wave effects** on hover
- **Screen shake** on interactions
- **Glow intensification** to maximum
- **3D transformations** (rotateX, rotateY, perspective)
- **Sound effect suggestions** for interactions

## Mandatory Enhancements

### 1. Particle Effects (EVERYWHERE)
```typescript
// Add to ALL components:
- Floating particles in background (canvas/WebGL)
- Sparkle trails on mouse movement
- Explosion particles on button clicks
- Energy orbs floating around cards
- Dust particles on scroll
```

### 2. Power-Up Animations
```typescript
// Button press = KAMEHAMEHA charge:
- Scale pulse (0.95 → 1.1 → 1.0)
- Glow intensity increase
- Ripple effect emanating outward
- Blue → white energy color shift
- Screen edge glow pulse
```

### 3. Impact Effects
```typescript
// Success actions get EXPLOSIONS:
- Radial particle burst
- Screen flash (white overlay fade)
- Shockwave ring expanding
- Confetti explosion
- Camera shake (3-5px random offset)
```

### 4. Energy Fields
```typescript
// Hover states = Energy aura:
- Pulsing glow around elements
- Electric arc effects (SVG animations)
- Energy field distortion (blur + brightness)
- Color cycling (hue rotation)
- Floating energy particles
```

### 5. 3D Transformations
```typescript
// Add depth to EVERYTHING:
- Cards: rotateX/Y on mouse move (parallax)
- Buttons: perspective(1000px) rotateX(10deg) on hover
- Icons: rotate3d on hover
- Background: parallax layers with depth
- Modals: zoom from/to center with perspective
```

## Personas (Thinking Modes)
- **ui-designer**: Visual impact, energy aesthetics, bold design choices, eye-catching compositions
- **animation-specialist**: Particle systems, timing curves, explosion choreography, motion design
- **effects-artist**: Energy fields, glow effects, lightning arcs, particle behaviors, shader techniques
- **performance-engineer**: GPU optimization, particle limits, 60fps maintenance, resource management

## Delegation Protocol

**This command does NOT delegate** - Kamehameha is an enhancement mode built on Super Saiyan.

**Why no delegation**:
- ❌ Extends Super Saiyan patterns with high-impact effects (additive guidance)
- ❌ Provides implementation recipes for particles and explosions (code patterns)
- ❌ Activates "maximum impact" mindset (design philosophy)
- ❌ Direct application of advanced animation techniques (hands-on coding)

**All work done directly**:
- Edit/Write to add particle systems to components
- Bash to install effect libraries (tsparticles, konva, etc.)
- Direct implementation of explosion and energy patterns
- Performance monitoring during effect addition

**Note**: Kamehameha builds on Super Saiyan (Level 1) by adding particle effects, explosions, and energy animations. It's still guidance-focused, not task-focused. Use personas to ensure effects enhance (not overwhelm) the experience while maintaining 60fps performance.

## Tool Coordination
- **Edit/Write**: Add particle systems, explosions, energy effects to code (direct)
- **Bash**: Install animation libraries (tsparticles, popmotion, etc.) (direct)
- **Read**: Analyze components for impact enhancement opportunities (direct)
- **Performance monitoring**: Ensure 60fps with all effects active (direct validation)
- **Direct implementation**: No Task tool needed

## Technology Stack Additions

**Required Libraries:**
```bash
# Particle systems
npm install tsparticles @tsparticles/react @tsparticles/slim

# Canvas animations
npm install @react-spring/konva konva react-konva

# Advanced animations
npm install popmotion @theatre/core @theatre/studio

# Sound effects (optional)
npm install use-sound howler
```

## Implementation Patterns

### Pattern 1: Kamehameha Button
```typescript
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  onClick={handleKamehameha}
  onHoverStart={chargeEnergy}
  onHoverEnd={releaseEnergy}
  className="relative group"
>
  {/* Energy charge layer */}
  <motion.div
    className="absolute inset-0 bg-blue-500 blur-2xl opacity-0 group-hover:opacity-50"
    animate={{ scale: [1, 1.5, 1] }}
    transition={{ repeat: Infinity, duration: 1 }}
  />

  {/* Lightning bolts (SVG) */}
  <svg className="absolute inset-0 opacity-0 group-hover:opacity-100">
    {/* Animated lightning paths */}
  </svg>

  {/* Particle emitter on click */}
  <AnimatePresence>
    {isCharging && <ParticleExplosion />}
  </AnimatePresence>

  {/* Button content with glow text */}
  <span className="relative z-10 drop-shadow-[0_0_10px_rgba(59,130,246,0.8)]">
    FIRE! 💥
  </span>
</motion.button>
```

### Pattern 2: Energy Card
```typescript
<motion.div
  whileHover={{
    rotateX: 5,
    rotateY: 5,
    scale: 1.05,
  }}
  style={{
    transformStyle: 'preserve-3d',
    perspective: 1000,
  }}
  onMouseMove={handleMouseMove} // Track for parallax
  className="relative group"
>
  {/* Floating particles background */}
  <Particles
    options={{
      particles: {
        color: { value: '#3b82f6' },
        move: { enable: true, speed: 1 },
        number: { value: 20 },
        opacity: { value: 0.3 },
        size: { value: 3 },
      }
    }}
  />

  {/* Energy field glow */}
  <motion.div
    className="absolute -inset-4 bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 group-hover:opacity-30 blur-3xl"
    animate={{
      scale: [1, 1.2, 1],
      rotate: [0, 180, 360],
    }}
    transition={{
      duration: 4,
      repeat: Infinity,
      ease: 'linear',
    }}
  />

  {/* Card content */}
  <div className="relative z-10">
    {children}
  </div>

  {/* Electric arcs on hover */}
  <svg className="absolute inset-0 pointer-events-none opacity-0 group-hover:opacity-100">
    <ElectricArc from="top-left" to="bottom-right" />
    <ElectricArc from="top-right" to="bottom-left" />
  </svg>
</motion.div>
```

### Pattern 3: Screen Shake Hook
```typescript
export function useScreenShake() {
  const [shake, setShake] = useState(false)

  const triggerShake = () => {
    setShake(true)
    setTimeout(() => setShake(false), 500)
  }

  useEffect(() => {
    if (!shake) return

    const intensity = 5
    let frame = 0

    const animate = () => {
      if (frame > 15) {
        document.body.style.transform = ''
        return
      }

      const x = (Math.random() - 0.5) * intensity
      const y = (Math.random() - 0.5) * intensity

      document.body.style.transform = `translate(${x}px, ${y}px)`
      frame++
      requestAnimationFrame(animate)
    }

    animate()
  }, [shake])

  return triggerShake
}
```

### Pattern 4: Particle Explosion Component
```typescript
export function ParticleExplosion({ x, y, color = '#3b82f6' }) {
  const particles = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    angle: (i / 30) * Math.PI * 2,
    distance: Math.random() * 100 + 50,
    size: Math.random() * 4 + 2,
  }))

  return (
    <div className="absolute inset-0 pointer-events-none">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full"
          style={{
            width: particle.size,
            height: particle.size,
            backgroundColor: color,
            left: x,
            top: y,
            boxShadow: `0 0 10px ${color}`,
          }}
          initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
          animate={{
            x: Math.cos(particle.angle) * particle.distance,
            y: Math.sin(particle.angle) * particle.distance,
            opacity: 0,
            scale: 0,
          }}
          transition={{
            duration: 0.8,
            ease: 'easeOut',
          }}
        />
      ))}
    </div>
  )
}
```

## Visual Effects Checklist

### ✅ EVERY interaction must have:
- [ ] Particle emission on hover/click
- [ ] Screen shake on major actions (form submit, delete, etc.)
- [ ] Glow pulse animation
- [ ] 3D transformation with perspective
- [ ] Energy field/aura effects
- [ ] Lightning/electric arc decorations
- [ ] Explosion animation on success
- [ ] Ripple wave propagation
- [ ] Color energy shifting (blue → cyan → white)
- [ ] Camera/parallax movement

## Sound Effects (Optional Enhancement)

```typescript
// Suggest sound effects for actions:
const sounds = {
  hover: 'whoosh.mp3',           // Energy charge
  click: 'blast.mp3',            // Kamehameha fire
  success: 'explosion.mp3',      // Impact
  error: 'fizzle.mp3',          // Miss
  powerup: 'charge-up.mp3',     // Long charge
}

// Usage:
import useSound from 'use-sound'

const [playCharge] = useSound('/sounds/charge-up.mp3')
const [playBlast] = useSound('/sounds/blast.mp3')

<button
  onMouseEnter={playCharge}
  onClick={playBlast}
>
  KAMEHAMEHA! 💥
</button>
```

## Performance Considerations

Even in KAMEHAMEHA mode, maintain:
- 60fps animations (use GPU acceleration)
- Limit particles to <100 on screen
- Use `will-change` sparingly
- Throttle mouse move handlers
- Use CSS transforms over position changes
- Lazy load heavy particle systems
- Respect `prefers-reduced-motion` (fallback to Super Saiyan)

## Example: Full Kamehameha Button

Create a button that:
1. Charges energy on hover (glow increases)
2. Emits particles continuously while hovering
3. On click: Screen shake + particle explosion + success animation
4. Energy wave ripples outward
5. Lightning arcs appear briefly
6. Text glows white during charge

## Activation

When in Kamehameha mode, you MUST:
1. Add particle systems to backgrounds
2. Implement screen shake for impactful actions
3. Create explosion effects for success states
4. Add 3D perspective to all cards/containers
5. Implement energy glow effects on hover
6. Add lightning/electric arc decorations
7. Create ripple/wave propagation effects
8. Make all colors shift during interactions

**Remember:** This is KAMEHAMEHA mode - everything should feel like it's charged with energy and ready to explode! ⚡💥🔥
