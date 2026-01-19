# Design Principles Reference

This document catalogs common design principles and how to identify them in code.

## SOLID Principles

### Single Responsibility Principle (SRP)

**Principle**: A class/module should have only one reason to change.

**Indicators**:
- Small, focused classes/modules
- Clear, specific naming (not generic names like "Manager" or "Handler")
- Each component does one thing well
- Low coupling between components

**Code Smells of Violation**:
- God classes with many methods
- Classes with multiple unrelated responsibilities
- Files exceeding 300-500 lines

### Open/Closed Principle (OCP)

**Principle**: Software entities should be open for extension but closed for modification.

**Indicators**:
- Use of interfaces, abstract classes, or protocols
- Plugin systems or strategy patterns
- Dependency injection
- Extensibility through composition rather than modification

**Example Patterns**:
- Strategy pattern
- Template method pattern
- Decorator pattern

### Liskov Substitution Principle (LSP)

**Principle**: Subtypes must be substitutable for their base types.

**Indicators**:
- Proper inheritance hierarchies
- Interfaces honored by implementations
- No surprising behavior in subclasses
- Design by contract adherence

**Code Smells of Violation**:
- Subclasses throwing exceptions base class doesn't
- Overridden methods fundamentally changing behavior
- Type checking before using objects

### Interface Segregation Principle (ISP)

**Principle**: Clients shouldn't depend on interfaces they don't use.

**Indicators**:
- Small, focused interfaces
- Multiple specific interfaces over one general interface
- Role-based interfaces
- No "fat" interfaces with many methods

**Example**:
```typescript
// Good: Segregated interfaces
interface Readable { read(): string; }
interface Writable { write(data: string): void; }

// Bad: Fat interface
interface FileOperations { 
  read(): string; 
  write(data: string): void;
  delete(): void;
  rename(name: string): void;
  // ... 20 more methods
}
```

### Dependency Inversion Principle (DIP)

**Principle**: Depend on abstractions, not concretions.

**Indicators**:
- Dependencies injected rather than instantiated
- Interfaces or abstract classes as dependencies
- Dependency injection framework usage
- Inversion of Control (IoC) containers

**Example**:
```python
# Good: Depend on abstraction
def process_data(storage: StorageInterface):
    storage.save(data)

# Bad: Depend on concrete class
def process_data(storage: MySQLDatabase):
    storage.save(data)
```

## Other Key Design Principles

### DRY (Don't Repeat Yourself)

**Principle**: Every piece of knowledge should have a single representation.

**Indicators**:
- Utility functions and shared modules
- Configuration centralization
- Template or base classes
- Code generation for repetitive patterns

**Code Smells of Violation**:
- Copy-pasted code blocks
- Similar functions with slight variations
- Duplicated business logic

### KISS (Keep It Simple, Stupid)

**Principle**: Simplicity should be a key goal; avoid unnecessary complexity.

**Indicators**:
- Straightforward, readable code
- Minimal abstraction layers
- Direct solutions over clever tricks
- Few dependencies

**Code Smells of Violation**:
- Over-engineering
- Premature optimization
- Unnecessary design patterns
- Complex abstractions for simple problems

### YAGNI (You Aren't Gonna Need It)

**Principle**: Don't add functionality until it's necessary.

**Indicators**:
- Minimal feature set
- No speculative abstractions
- Features driven by actual requirements
- Incremental development

**Code Smells of Violation**:
- Unused code or commented-out code
- "Just in case" features
- Overly generic frameworks

### Separation of Concerns (SoC)

**Principle**: Separate program into distinct sections addressing different concerns.

**Indicators**:
- Clear module boundaries
- Each module addresses specific functionality
- Minimal overlap between modules
- Layered architecture

**Examples**:
- Presentation logic separate from business logic
- Data access separate from business rules
- Configuration separate from code

### Law of Demeter (Principle of Least Knowledge)

**Principle**: A unit should have limited knowledge about other units.

**Indicators**:
- Methods only call methods on:
  - Itself
  - Objects passed as parameters
  - Objects it creates
  - Directly held components
- No train wrecks: `object.getX().getY().getZ()`

**Example**:
```java
// Good: Follow Law of Demeter
customer.getPurchase();

// Bad: Chain calls
customer.getWallet().getMoney().getAmount();
```

### Composition Over Inheritance

**Principle**: Favor object composition over class inheritance.

**Indicators**:
- Interfaces and dependency injection
- Strategy or decorator patterns
- Mixins or traits
- Flat inheritance hierarchies

**Code Smells of Violation**:
- Deep inheritance trees (>3-4 levels)
- Fragile base class problem
- Difficulty understanding class hierarchy

### Principle of Least Astonishment

**Principle**: Components should behave as users expect.

**Indicators**:
- Intuitive naming
- Consistent API design
- Expected behavior from functions
- Clear error messages

**Code Smells of Violation**:
- Misleading function names
- Side effects in getters
- Inconsistent return types
- Surprising exceptions

### Fail Fast

**Principle**: Errors should be detected and reported as early as possible.

**Indicators**:
- Input validation at boundaries
- Precondition checks
- Type systems (TypeScript, Rust, etc.)
- Immediate error reporting

**Example**:
```python
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
```

### Convention Over Configuration

**Principle**: Reduce decisions by providing sensible defaults.

**Indicators**:
- Minimal configuration files
- Directory structure conventions
- Naming conventions that drive behavior
- Zero-config setups

**Common in**: Rails, Maven, Next.js

### Immutability

**Principle**: Objects should not change state after creation.

**Indicators**:
- `const`, `final`, `readonly` keywords
- Functional programming style
- No setter methods
- Copy-on-write patterns

**Benefits**:
- Thread safety
- Easier reasoning about code
- Predictable behavior

## Design Philosophy Indicators

### Performance-Focused

**Indicators**:
- Benchmarking code and performance tests
- Memory pooling or object reuse
- Careful algorithm selection (O(n) complexity comments)
- Profiling hooks
- Zero-copy or zero-allocation patterns
- Comments about performance trade-offs

### Developer Experience (DX) Focused

**Indicators**:
- Extensive documentation and examples
- Helpful error messages
- CLI with good help text
- Type definitions and IDE support
- Quick start guides
- Convention over configuration

### Security-First

**Indicators**:
- Input sanitization everywhere
- Security audit logs
- Principle of least privilege
- Dependencies regularly updated
- Security-focused comments (SECURITY:, XXE:, etc.)
- Constant-time comparison functions

### Test-Driven Development (TDD)

**Indicators**:
- High test coverage (>80%)
- Tests as documentation
- Test files mirror source structure
- Fast test suite
- Mocking and dependency injection

### Domain-Driven Design (DDD)

**Indicators**:
- Ubiquitous language in code
- Bounded contexts
- Aggregates and entities clearly defined
- Repository pattern
- Domain events
- Rich domain models (not anemic)

### Functional Programming

**Indicators**:
- Pure functions
- Immutable data structures
- Higher-order functions
- Function composition
- Minimal side effects
- Declarative over imperative style

### Object-Oriented Programming

**Indicators**:
- Encapsulation (private fields, public methods)
- Inheritance hierarchies
- Polymorphism usage
- Design patterns (Factory, Builder, Observer, etc.)
- Object lifecycle management

## Identifying Trade-offs

When analyzing design decisions, look for these common trade-offs:

### Performance vs. Maintainability
- Optimized code often more complex
- Look for comments explaining performance hacks

### Flexibility vs. Simplicity
- Generic solutions more complex but reusable
- Check if abstraction matches actual use cases

### Speed of Development vs. Code Quality
- Technical debt markers (TODO, FIXME, HACK)
- Missing tests or documentation

### Type Safety vs. Dynamic Flexibility
- Strict typing vs. dynamic languages
- Runtime checks vs. compile-time guarantees

### Consistency vs. Pragmatism
- Exceptions to architectural rules
- Comments like "breaking pattern here because..."

## How to Extract Design Philosophy

1. **Read design documents**: Check docs/, ADRs, RFCs
2. **Examine git history**: Look at major refactorings and their commit messages
3. **Study the testing approach**: Test quality reveals priorities
4. **Review PR discussions**: GitHub issues and PRs show decision-making
5. **Look for trade-off comments**: Comments explaining "why" over "what"
6. **Check dependencies**: Choice of libraries reveals philosophy
7. **Analyze error handling**: Fail-fast vs. defensive vs. graceful degradation
