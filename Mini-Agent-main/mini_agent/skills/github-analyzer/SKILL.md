---
name: github-analyzer
description: Deep analysis of GitHub repositories to understand their core architecture, design philosophy, technical decisions, and implementation patterns. This skill should be used when users provide a GitHub URL and request comprehensive understanding of the repository's structure, purpose, key abstractions, or technical approach.
---

# GitHub Analyzer

## Overview

This skill provides a systematic methodology for deeply understanding GitHub repositories by analyzing their architecture, design philosophy, implementation patterns, and technical decisions. It adapts analysis depth based on repository size and complexity, providing both high-level architectural insights and detailed implementation understanding.

## When to Use This Skill

Use this skill when:
- User provides a GitHub URL and asks to "understand this repo"
- User requests analysis of a repository's design philosophy or core concepts
- User wants to know the technical stack, architecture patterns, or key abstractions
- User asks about how a specific open-source project is structured or works
- User needs to evaluate a repository for learning, contribution, or adoption decisions

**Trigger patterns:**
- "Analyze this GitHub repo: [URL]"
- "Help me understand how [project] works"
- "What's the architecture of [GitHub URL]?"
- "Explain the design philosophy behind [repo]"
- "What are the core concepts in this repository?"

## Analysis Methodology

### Phase 1: Initial Repository Assessment

Start by gathering high-level context to understand scope and complexity:

1. **Clone or fetch the repository** (if not already local)
   - Use `gh repo clone` or `git clone` to get the repository locally
   - If repository is very large (>500MB), consider shallow clone: `git clone --depth=1`

2. **Perform quick reconnaissance**
   - Read README.md, CONTRIBUTING.md, ARCHITECTURE.md, and any docs/ folder
   - Check package.json, setup.py, Cargo.toml, go.mod, or equivalent for tech stack
   - Run `tokei` or similar tool to understand language distribution and LOC
   - Review directory structure using `tree -L 3` or `ls -la`

3. **Determine analysis depth strategy**
   - **Small repos (<5k LOC)**: Full comprehensive analysis of all files
   - **Medium repos (5k-50k LOC)**: Focus on core modules, skip boilerplate/tests initially
   - **Large repos (>50k LOC)**: Strategic sampling of key modules, heavy reliance on documentation

### Phase 2: Architecture Discovery

Understand the high-level system design:

1. **Identify architectural patterns**
   - Look for common patterns: MVC, microservices, event-driven, layered architecture
   - Identify separation of concerns: frontend/backend, core/plugins, lib/cli
   - Note any architectural documentation or diagrams

2. **Map core abstractions and modules**
   - Identify the main entities/models/data structures
   - Find the primary interfaces, traits, or protocols
   - Understand module boundaries and dependencies
   - Use `references/architecture_patterns.md` for common pattern recognition

3. **Trace data flow and control flow**
   - Identify entry points (main functions, API routes, CLI commands)
   - Follow the execution path for typical operations
   - Understand how data moves through the system

### Phase 3: Design Philosophy Analysis

Extract the "why" behind technical decisions:

1. **Read design documents and RFCs**
   - Check for docs/design/, docs/rfcs/, or ADR (Architecture Decision Records)
   - Review commit messages for major architectural changes
   - Look for blog posts or talks linked in README

2. **Identify design principles**
   - Performance vs. simplicity trade-offs
   - Extensibility mechanisms (plugins, hooks, middleware)
   - Error handling philosophy (fail-fast, defensive, graceful degradation)
   - Use `references/design_principles.md` for common patterns

3. **Understand constraints and priorities**
   - Target platforms (web, mobile, embedded)
   - Performance requirements
   - Security considerations
   - Developer experience priorities

### Phase 4: Technical Stack Deep Dive

Analyze technology choices and their implications:

1. **Primary technologies**
   - Programming languages and their usage (e.g., TypeScript for type safety)
   - Frameworks and libraries (React, Express, Django, etc.)
   - Build tools and development workflow

2. **Infrastructure and deployment**
   - Database choices and data modeling
   - Caching strategies
   - CI/CD setup (GitHub Actions, Travis, etc.)
   - Deployment targets (Docker, serverless, native binaries)

3. **Dependencies and ecosystem**
   - Key dependencies and why they were chosen
   - Version constraints and compatibility requirements
   - Internal vs. external dependencies

### Phase 5: Implementation Patterns

Study how code is structured and organized:

1. **Code organization patterns**
   - File and directory naming conventions
   - Module structure and imports
   - Code style and formatting standards

2. **Common implementation idioms**
   - How errors are handled
   - How configuration is managed
   - How testing is approached
   - How logging and observability work

3. **Key algorithms and data structures**
   - Performance-critical sections
   - Novel or interesting implementations
   - Use of standard vs. custom solutions

## Analysis Output Structure

Present findings in a structured format:

### 1. Executive Summary
- Project purpose in 2-3 sentences
- Primary use cases
- Key differentiators or unique aspects

### 2. Architecture Overview
- High-level architecture diagram (ASCII art or description)
- Core modules and their responsibilities
- Architectural patterns identified
- System boundaries and interfaces

### 3. Design Philosophy
- Core design principles
- Trade-offs and priorities
- Why certain approaches were chosen
- Constraints that shaped the design

### 4. Technical Stack
- Languages and frameworks with justification
- Key dependencies and their roles
- Build and deployment approach
- Performance and scalability considerations

### 5. Implementation Highlights
- Directory structure explanation
- Entry points and main workflows
- Notable code patterns or idioms
- Testing and quality assurance approach

### 6. Code Navigation Guide
- Where to find key functionality
- Most important files to understand
- Suggested reading order for newcomers
- References to external documentation

## Adaptive Analysis Strategies

### For Small Repositories (<5k LOC)
- Read all core source files completely
- Trace through actual code execution paths
- Provide detailed code-level insights
- Include specific function/class references

### For Medium Repositories (5k-50k LOC)
- Focus on core modules, read selectively
- Use grep/search to find key implementations
- Sample representative code from each major component
- Balance breadth and depth

### For Large Repositories (>50k LOC)
- Heavy reliance on documentation
- Strategic sampling of critical paths
- Use search to answer specific questions
- Focus on architectural understanding over implementation details
- Leverage existing diagrams and design docs

## Handling Specific Repository Types

### Web Applications
- Frontend architecture (components, state management, routing)
- Backend API design (REST, GraphQL, RPC)
- Data layer (ORM, query builders, migrations)
- Authentication and authorization approach

### CLI Tools
- Command structure and argument parsing
- Configuration management
- User interaction patterns
- Plugin or extension system

### Libraries/Frameworks
- Public API surface and design
- Internal abstractions and extension points
- Usage examples and typical workflows
- Documentation quality and completeness

### System Software
- Performance-critical sections
- Memory management approach
- Concurrency and parallelism patterns
- Platform-specific considerations

## Resources

### references/

- `architecture_patterns.md` - Common architectural patterns and how to identify them
- `design_principles.md` - Catalog of design principles and their indicators in code

### scripts/

- `repo_stats.py` - Generate repository statistics (LOC, file counts, language distribution)
- `dependency_analyzer.py` - Analyze and visualize dependency graphs

## Best Practices

1. **Start broad, then narrow**: Begin with documentation and high-level structure before diving into code
2. **Follow the data**: Understanding data structures often reveals system design
3. **Look for tests**: Well-written tests explain intended behavior
4. **Check git history**: Major commits often explain architectural decisions
5. **Use search strategically**: grep for TODO, FIXME, NOTE comments for insights
6. **Consider the audience**: Adapt explanation depth to user's expertise level
7. **Be honest about gaps**: If the repository is too large or complex, acknowledge limitations
