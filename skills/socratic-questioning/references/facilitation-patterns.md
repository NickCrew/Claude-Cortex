# Facilitation Patterns Reference

Patterns for facilitating discovery of Clean Code principles, GoF design patterns,
architectural trade-offs, and refactoring opportunities through questioning.

## Clean Code Discovery Questions

### Meaningful Names

| Code smell | Discovery question | Follow-up |
|-----------|-------------------|-----------|
| Single-letter variable | "What does `d` represent? How long did it take you to figure that out?" | "What name would make it immediately obvious?" |
| Misleading name | "Does this function name accurately describe everything it does?" | "If someone called this function based on its name alone, would they be surprised by its behavior?" |
| Inconsistent conventions | "In this file, I see `getUserData`, `fetch_account`, and `loadProfile`. What pattern do you notice?" | "What would consistency look like?" |
| Magic numbers | "What does the number `86400` mean here?" | "How would you make this self-documenting?" |

### Functions

| Code smell | Discovery question | Follow-up |
|-----------|-------------------|-----------|
| Long function | "If you had to explain this function's purpose in one sentence, how many sentences would you actually need?" | "What if each sentence became its own function?" |
| Many parameters | "How many things do you need to know to call this function?" | "What would it look like if related parameters were grouped?" |
| Side effects | "Does this function do anything beyond what its name promises?" | "What could go wrong if a caller doesn't expect that hidden behavior?" |
| Mixed abstraction levels | "Some of these lines deal with business logic, others with HTTP details. What do you notice?" | "What if each abstraction level had its own layer?" |

### Error Handling

| Code smell | Discovery question | Follow-up |
|-----------|-------------------|-----------|
| Returning null | "What happens to the caller when this returns null?" | "How many places need to check for null? What if you threw an exception instead?" |
| Swallowed exception | "What happens when this catch block runs?" | "If this error occurred in production, how would you know?" |
| String error codes | "How does the caller know which error happened?" | "What would typed exceptions give you that strings don't?" |

### Classes

| Code smell | Discovery question | Follow-up |
|-----------|-------------------|-----------|
| God class | "If you listed everything this class is responsible for, how long would the list be?" | "Which responsibilities could live in their own class?" |
| Low cohesion | "Do all the methods in this class use the same fields?" | "What does it tell you when a method ignores most of the class's state?" |
| Tight coupling | "If you changed the database, how many files would you need to modify?" | "What would it look like if this class didn't know about the database at all?" |

---

## GoF Pattern Discovery

### Strategy Pattern

**When to suggest**: The learner has a switch/case or if/else chain that selects behavior based on a type.

```
Q: "What happens when you need to add a new [type/behavior]?"
A: [Learner realizes they have to modify the existing function]
Q: "What if each behavior was its own object that you could swap in?"
A: [Learner describes the Strategy pattern without naming it]
→ "That's the Strategy pattern. The behavior varies independently from the client."
```

### Observer Pattern

**When to suggest**: The learner has code where one object needs to notify many others when something changes.

```
Q: "How does [component A] know when [component B] changes?"
A: [Learner describes polling or direct calls]
Q: "What if B didn't need to know who was listening — just that someone might be?"
A: [Learner describes a notification mechanism]
→ "That's the Observer pattern. Publishers don't know their subscribers."
```

### Factory Method / Abstract Factory

**When to suggest**: The learner has object creation logic scattered or duplicated, or creation depends on runtime conditions.

```
Q: "How many places in the code create [this type of object]?"
A: [Learner finds duplication]
Q: "What if there was one place responsible for deciding which concrete type to create?"
A: [Learner proposes centralized creation]
→ "That's the Factory pattern. It encapsulates object creation."
```

### Decorator Pattern

**When to suggest**: The learner wants to add behavior to an object without modifying its class.

```
Q: "You want to add logging to this service. What if you also need caching later? And retry logic?"
A: [Learner sees potential for class explosion with inheritance]
Q: "What if you could wrap the original object, adding one behavior at a time?"
A: [Learner describes wrapping/layering]
→ "That's the Decorator pattern. Each wrapper adds one responsibility."
```

### Adapter Pattern

**When to suggest**: The learner needs to use a class whose interface doesn't match what the caller expects.

```
Q: "Your code expects [interface A], but the library provides [interface B]. What are your options?"
A: [Learner considers modifying the caller or the library]
Q: "What if you wrote a thin translation layer between the two?"
A: [Learner describes the adapter concept]
→ "That's the Adapter pattern. It translates one interface to another."
```

### Command Pattern

**When to suggest**: The learner needs to queue, log, or undo operations.

```
Q: "How would you implement undo for this action?"
A: [Learner struggles with saving state]
Q: "What if each action was an object that knew how to execute itself — and reverse itself?"
A: [Learner describes encapsulated actions]
→ "That's the Command pattern. Actions become first-class objects."
```

---

## Architectural Trade-Off Exploration

### Guiding Trade-Off Discussions

When developers face architectural decisions, use questions to surface trade-offs
rather than prescribing a solution:

```
Q: "What does this approach optimize for?"
Q: "What are you giving up to get that?"
Q: "How would this decision look in 6 months with 10x the traffic?"
Q: "What's the simplest version that still solves the problem?"
Q: "What would make you reverse this decision?"
```

### Common Trade-Off Pairs

| Trade-off | Discovery questions |
|-----------|-------------------|
| **Consistency vs Availability** | "What happens to users if this service is briefly inconsistent? What happens if it's unavailable?" |
| **Simplicity vs Flexibility** | "How likely is it that you'll need this flexibility? What does the extra abstraction cost you today?" |
| **Performance vs Readability** | "Is this optimization measurably necessary, or is it premature?" |
| **DRY vs Decoupling** | "These two modules share code, but do they change for the same reasons?" |
| **Build vs Buy** | "How much of this is truly unique to your domain vs commodity infrastructure?" |

---

## Refactoring Discovery

### Code Smell Identification Through Questioning

Instead of pointing out smells, guide discovery:

| Smell | Question chain |
|-------|---------------|
| **Duplicated code** | "What happens if you need to change this logic?" → "How many places would you need to update?" → "What does that tell you?" |
| **Long method** | "Can you describe what this method does in one sentence?" → "How many 'and's did you use?" → "What if each 'and' was its own method?" |
| **Feature envy** | "Which class's data does this method use the most?" → "What if the method lived in that class instead?" |
| **Data clumps** | "How many times do you see these three parameters together?" → "What if they were a single object?" |
| **Primitive obsession** | "What does this string represent? What values are valid?" → "What would a dedicated type give you?" |
| **Shotgun surgery** | "When you change [feature], how many files do you touch?" → "What if all those changes were in one place?" |

### Refactoring Readiness Assessment

Before suggesting a refactoring, confirm readiness:

```
Q: "Do you have tests covering this code?"
Q: "What's the smallest change that would improve this?"
Q: "If this refactoring introduced a bug, how quickly would you find it?"
Q: "Is this the right time to refactor, or should it wait for a dedicated effort?"
```

These questions help the learner internalize the discipline of safe refactoring -- test coverage first, small steps, and timing awareness.
