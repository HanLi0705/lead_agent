# Architecture Patterns Reference

This document catalogs common architectural patterns and how to identify them in codebases.

## Layered Architecture

**Description**: System organized into horizontal layers, each providing services to the layer above.

**Indicators**:
- Directory structure like: `presentation/`, `business/`, `data/`, `database/`
- Or: `ui/`, `service/`, `repository/`, `model/`
- Clear separation between UI, business logic, and data access
- Dependencies flow downward (upper layers depend on lower layers)

**Common in**: Enterprise applications, web applications, monolithic systems

**Example Structure**:
```
src/
├── presentation/    # UI, controllers, views
├── business/        # Business logic, use cases
├── data/           # Data access, repositories
└── domain/         # Core domain models
```

## Microservices Architecture

**Description**: Application composed of small, independently deployable services.

**Indicators**:
- Multiple service directories or repositories
- Each service has its own database/storage
- API gateway or service mesh configuration
- Docker/Kubernetes deployment files
- Service discovery mechanisms

**Common in**: Large-scale distributed systems, cloud-native applications

**Example Structure**:
```
services/
├── user-service/
├── order-service/
├── payment-service/
└── notification-service/
```

## Model-View-Controller (MVC)

**Description**: Separates application into three interconnected components.

**Indicators**:
- `models/`, `views/`, `controllers/` directories
- Or similar naming: `entities/`, `templates/`, `handlers/`
- Models represent data and business logic
- Views handle presentation
- Controllers coordinate between models and views

**Common in**: Web frameworks (Rails, Django, Spring MVC)

**Example Structure**:
```
app/
├── models/         # Data models and business logic
├── views/          # Templates and UI components
└── controllers/    # Request handlers and routing
```

## Event-Driven Architecture

**Description**: Communication between components happens through events.

**Indicators**:
- Event bus, message queue, or pub/sub system
- Event handlers, subscribers, or listeners
- Files named like `*Event.js`, `*Handler.py`, `*Subscriber.go`
- Message broker configuration (Kafka, RabbitMQ, Redis)

**Common in**: Real-time systems, reactive applications, distributed systems

**Example Patterns**:
- `EventEmitter` or `EventBus` classes
- Observer pattern implementation
- Command Query Responsibility Segregation (CQRS)

## Hexagonal Architecture (Ports and Adapters)

**Description**: Application core is isolated from external concerns through ports and adapters.

**Indicators**:
- `core/`, `domain/`, or `application/` containing business logic
- `adapters/`, `infrastructure/`, or `ports/` for external integrations
- Dependency injection heavily used
- Interfaces/abstractions separating core from infrastructure

**Common in**: Domain-driven design, clean architecture implementations

**Example Structure**:
```
src/
├── domain/          # Core business logic
├── application/     # Use cases
├── adapters/        # External integrations
│   ├── http/
│   ├── database/
│   └── messaging/
└── ports/           # Interfaces
```

## Plugin Architecture

**Description**: Core system with extensibility through plugins.

**Indicators**:
- `plugins/`, `extensions/`, or `addons/` directory
- Plugin loader or registry
- Well-defined plugin API or interface
- Configuration for enabling/disabling plugins

**Common in**: Extensible applications, tools, IDEs

**Example Patterns**:
- Plugin manifest files (JSON, YAML)
- Hook system for plugin integration
- Dynamic loading mechanisms

## Pipe and Filter

**Description**: Data flows through a series of processing steps.

**Indicators**:
- `filters/`, `processors/`, `transformers/`, or `middleware/` directories
- Chain of responsibility pattern
- Stream processing
- Data transformation pipelines

**Common in**: Data processing systems, compilers, build tools

**Example Structure**:
```
src/
├── filters/
│   ├── validation.js
│   ├── transformation.js
│   └── enrichment.js
└── pipeline.js
```

## Client-Server Architecture

**Description**: Clients make requests to servers which process and respond.

**Indicators**:
- Separate `client/` and `server/` directories
- API endpoints and routes
- Client-side and server-side rendering code
- Network communication layer

**Common in**: Web applications, networked applications

## Service-Oriented Architecture (SOA)

**Description**: Functionality organized into discrete services with well-defined interfaces.

**Indicators**:
- Service contracts or interface definitions (WSDL, OpenAPI)
- Service registry or discovery
- Enterprise service bus (ESB)
- Multiple service implementations

**Common in**: Enterprise systems, legacy modernization

## Repository Pattern

**Description**: Abstraction layer between data access logic and business logic.

**Indicators**:
- `repositories/` or `dao/` (Data Access Object) directories
- Interfaces defining data operations
- Separation of domain models from database entities
- Unit of Work pattern often present

**Common in**: Applications using ORM, domain-driven design

**Example**:
```typescript
interface UserRepository {
  findById(id: string): User;
  save(user: User): void;
  delete(id: string): void;
}
```

## CQRS (Command Query Responsibility Segregation)

**Description**: Separate models for reading and writing data.

**Indicators**:
- `commands/` and `queries/` directories
- Separate read and write models
- Command handlers and query handlers
- Event sourcing often combined

**Common in**: Complex domains, event-driven systems

## Clean Architecture

**Description**: Concentric circles of dependencies flowing inward toward business logic.

**Indicators**:
- `entities/`, `use-cases/`, `interface-adapters/`, `frameworks/` layers
- Dependency rule: inner layers don't know about outer layers
- Interfaces at boundaries
- Framework and tool independence

**Example Structure**:
```
src/
├── entities/           # Enterprise business rules
├── use-cases/          # Application business rules
├── interface-adapters/ # Controllers, presenters, gateways
└── frameworks/         # External frameworks and tools
```

## Pattern Identification Tips

1. **Start with directory structure**: Often reflects architectural intent
2. **Look for README or ARCHITECTURE.md**: Explicit documentation of patterns
3. **Examine dependencies**: How components depend on each other
4. **Find entry points**: Main files reveal high-level organization
5. **Check configuration**: Deployment and build configs hint at architecture
6. **Review tests**: Test structure often mirrors application architecture
