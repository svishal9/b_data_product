# SCB Data Product - Architecture Documentation Index

## 🎯 Quick Navigation

### I Want To...

**Understand the architecture**
→ Start: [`ARCHITECTURE_VISUAL_SUMMARY.md`](./ARCHITECTURE_VISUAL_SUMMARY.md)
→ Then: [`PROJECT_ARCHITECTURE.md`](./PROJECT_ARCHITECTURE.md)
→ Deep: [`ARCHITECTURE_DEEP_DIVE.md`](./ARCHITECTURE_DEEP_DIVE.md)

**See how components interact**
→ Read: [`COMPONENT_INTERACTION_DIAGRAM.md`](./COMPONENT_INTERACTION_DIAGRAM.md)

**Get started quickly**
→ Follow: [`QUICK_START_ENTITIES.md`](./QUICK_START_ENTITIES.md)

**Learn about entity types**
→ Reference: [`ENTITY_TYPES.md`](./ENTITY_TYPES.md)

**Work with data models**
→ Guide: [`PYDANTIC_MODELS_GUIDE.md`](./PYDANTIC_MODELS_GUIDE.md)

**Find something specific**
→ Use: [`ARCHITECTURE_QUICK_REFERENCE.md`](./ARCHITECTURE_QUICK_REFERENCE.md)

---

## 📚 Documentation Catalog

<a name="architecture-visual-summary"></a>

### 1. **ARCHITECTURE_VISUAL_SUMMARY.md**
**Purpose**: Single-page visual reference
**Content**:
- Six-tier architecture diagram
- Component relationships (dependency graph)
- Module count by layer
- Data flow lifecycle
- Class hierarchies
- Communication patterns
- Technology stack
- Architecture strengths/weaknesses
- Integration points
- Deployment topology
- Performance characteristics

**Best For**: Getting a bird's-eye view, quick lookups, presentations

**Key Sections**:
- Single-Page Architecture Overview
- Component Relationships
- Technology Stack
- Architecture Strengths
- Deployment Architecture

---

<a name="project-architecture"></a>

### 2. **PROJECT_ARCHITECTURE.md**
**Purpose**: Comprehensive architecture overview
**Content**:
- System architecture with diagrams
- Detailed project structure (full tree)
- Core component descriptions
- Data flow for each operation
- Design patterns used
- Technology stack table
- Integration points
- Extensibility guide
- Testing architecture

**Best For**: Understanding the system end-to-end, planning changes

**Key Sections**:
- System Architecture
- Project Structure
- Core Components (1-6)
- Data Flow
- Design Patterns
- Technology Stack
- Integration Points

---

<a name="architecture-deep-dive"></a>

### 3. **ARCHITECTURE_DEEP_DIVE.md**
**Purpose**: Detailed patterns and hierarchies
**Content**:
- Complete package hierarchy
- Type system architecture
- Entity lifecycle (create, update, delete)
- Data model composition
- Service layer design patterns
- Error handling strategy
- Configuration strategy
- Testing architecture
- Module dependencies

**Best For**: Deep understanding, implementing features, debugging

**Key Sections**:
- Package Structure Hierarchy
- Type System Architecture
- Entity Lifecycle
- Data Model Architecture
- Service Layer Design
- Error Handling Strategy

---

<a name="component-interaction-diagram"></a>

### 4. **COMPONENT_INTERACTION_DIAGRAM.md**
**Purpose**: Visual interactions and data flows
**Content**:
- Component interaction diagram
- Data flow interactions (sequences)
- Module dependencies map
- Deployment topology
- Class hierarchy diagrams
- API contract examples
- Performance considerations

**Best For**: Understanding how components work together, visualizing flows

**Key Sections**:
- Component Architecture Overview
- Data Flow Interactions (4 flows)
- Module Dependencies
- Deployment Topology
- Class Hierarchy
- API Contract Summary

---

<a name="quick-start-entities"></a>

### 5. **QUICK_START_ENTITIES.md** (Provided)
**Purpose**: Hands-on getting started guide
**Content**:
- What was added (4 new entity types)
- How to use (Builders and Service functions)
- Files added/modified
- Getting started steps
- Example workflow
- Data lineage
- Troubleshooting

**Best For**: First-time users, practical examples

**Key Sections**:
- What Was Added
- How to Use
- Files Added/Modified
- Getting Started
- Example Workflow

---

<a name="entity-types"></a>

### 6. **ENTITY_TYPES.md** (Project file)
**Purpose**: Complete entity type reference
**Content**:
- Entity type specifications
- ENUM type definitions
- Struct type definitions
- Relationship definitions
- Classification definitions
- Usage examples for all types
- Best practices
- Troubleshooting

**Best For**: API reference, type definitions, creating custom types

**Note**: Refer to existing project file for complete details

---

<a name="pydantic-models-guide"></a>

### 7. **PYDANTIC_MODELS_GUIDE.md** (Project file)
**Purpose**: Data models documentation
**Content**:
- Data model overview
- Model validation patterns
- Composition examples
- Error handling in models
- Custom validators
- Model usage examples
- Best practices

**Best For**: Working with Pydantic models, validation

**Note**: Refer to existing project file for complete details

---

<a name="architecture-quick-reference"></a>

### 8. **ARCHITECTURE_QUICK_REFERENCE.md**
**Purpose**: Quick lookup and cheat sheet
**Content**:
- File organization map
- Layer responsibilities
- Key design patterns
- Data flow reference
- Module import map
- Configuration reference
- Common usage patterns
- Service function reference
- Type definitions available
- Testing reference
- Common commands
- Troubleshooting table
- Glossary

**Best For**: Quick lookups, copy-paste code, troubleshooting

**Key Sections**:
- File Organization Map
- Layer Responsibilities
- Common Usage Patterns
- Service Function Reference
- Troubleshooting Quick Reference

---

## 🗺️ Documentation Structure Map

```
Documentation
│
├── Quick Reference (Start here if learning)
│   ├── ARCHITECTURE_VISUAL_SUMMARY.md (visuals)
│   └── ARCHITECTURE_QUICK_REFERENCE.md (cheat sheet)
│
├── Core Architecture (Comprehensive understanding)
│   ├── PROJECT_ARCHITECTURE.md (overview)
│   ├── ARCHITECTURE_DEEP_DIVE.md (details)
│   └── COMPONENT_INTERACTION_DIAGRAM.md (flows)
│
├── Practical Guides (How to do things)
│   ├── QUICK_START_ENTITIES.md (getting started)
│   ├── ENTITY_TYPES.md (entity reference)
│   ├── PYDANTIC_MODELS_GUIDE.md (data models)
│   └── README.md (installation)
│
└── Reference (Look things up)
    ├── Code files (implementation)
    └── Test files (examples)
```

---

## 📖 Reading Paths

### Path 1: Learning the Architecture (Complete)
1. Start: `ARCHITECTURE_VISUAL_SUMMARY.md` (15 min)
2. Overview: `PROJECT_ARCHITECTURE.md` (30 min)
3. Details: `ARCHITECTURE_DEEP_DIVE.md` (45 min)
4. Flows: `COMPONENT_INTERACTION_DIAGRAM.md` (30 min)
5. Reference: `ARCHITECTURE_QUICK_REFERENCE.md` (20 min)
**Total Time**: ~2.5 hours, **Result**: Deep architecture understanding

### Path 2: Getting Started (Fast)
1. Visual: `ARCHITECTURE_VISUAL_SUMMARY.md` (15 min)
2. Quick Start: `QUICK_START_ENTITIES.md` (20 min)
3. Reference: `ARCHITECTURE_QUICK_REFERENCE.md` (15 min)
4. Code: Try examples from QUICK_START_ENTITIES.md (30 min)
**Total Time**: ~1.5 hours, **Result**: Can create entities

### Path 3: Specific Task (Focused)
1. Lookup: Find task in `ARCHITECTURE_QUICK_REFERENCE.md`
2. Pattern: Look up pattern in `COMPONENT_INTERACTION_DIAGRAM.md`
3. Deep Dive: Check details in `ARCHITECTURE_DEEP_DIVE.md`
4. Code: Look at actual implementation
**Total Time**: 15-30 min per task, **Result**: Task completed

### Path 4: Troubleshooting (Quick Fix)
1. Problem: Check `ARCHITECTURE_QUICK_REFERENCE.md` troubleshooting table
2. Context: If not found, check relevant section in `ARCHITECTURE_DEEP_DIVE.md`
3. Code: Look at actual implementation or tests
**Total Time**: 5-15 min, **Result**: Issue resolved

---

## 🔍 Finding Information

### By Topic

**"I want to understand the overall system"**
- `ARCHITECTURE_VISUAL_SUMMARY.md` → Single-page diagram
- `PROJECT_ARCHITECTURE.md` → Complete overview

**"How do I create an entity?"**
- `QUICK_START_ENTITIES.md` → Example workflow
- `ARCHITECTURE_QUICK_REFERENCE.md` → Common usage patterns
- `COMPONENT_INTERACTION_DIAGRAM.md` → Creation sequence

**"What types and enums are available?"**
- `ENTITY_TYPES.md` → Complete reference
- `ARCHITECTURE_QUICK_REFERENCE.md` → Summary table

**"How do I validate data?"**
- `PYDANTIC_MODELS_GUIDE.md` → Data models
- `ARCHITECTURE_DEEP_DIVE.md` → Model validation pattern

**"What's the file structure?"**
- `ARCHITECTURE_QUICK_REFERENCE.md` → File organization map
- `ARCHITECTURE_DEEP_DIVE.md` → Package structure hierarchy

**"How do services work?"**
- `COMPONENT_INTERACTION_DIAGRAM.md` → Service interaction
- `ARCHITECTURE_DEEP_DIVE.md` → Service layer design

**"What error handling is available?"**
- `ARCHITECTURE_DEEP_DIVE.md` → Error handling strategy
- `ARCHITECTURE_QUICK_REFERENCE.md` → Exception reference

**"How do I run tests?"**
- `ARCHITECTURE_QUICK_REFERENCE.md` → Testing reference
- `PROJECT_ARCHITECTURE.md` → Testing architecture

**"What are the design patterns?"**
- `PROJECT_ARCHITECTURE.md` → Design patterns section
- `ARCHITECTURE_DEEP_DIVE.md` → Patterns in detail

---

## 📊 Documentation Comparison

```
┌─────────────────────────────┬──────────┬──────────┬─────────┐
│ Document                    │ Breadth  │ Depth    │ Purpose │
├─────────────────────────────┼──────────┼──────────┼─────────┤
│ VISUAL_SUMMARY              │ ⭐⭐⭐⭐⭐ │ ⭐⭐     │ Overview│
│ PROJECT_ARCHITECTURE        │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐⭐ │ Complete│
│ ARCHITECTURE_DEEP_DIVE      │ ⭐⭐⭐   │ ⭐⭐⭐⭐⭐ │ Details │
│ COMPONENT_INTERACTION       │ ⭐⭐⭐⭐ │ ⭐⭐⭐⭐ │ Flows   │
│ QUICK_REFERENCE             │ ⭐⭐⭐⭐⭐ │ ⭐⭐     │ Lookup  │
│ QUICK_START_ENTITIES        │ ⭐⭐     │ ⭐⭐⭐   │ Tutorial│
│ ENTITY_TYPES                │ ⭐⭐⭐   │ ⭐⭐⭐   │ API Ref │
│ PYDANTIC_MODELS_GUIDE       │ ⭐⭐⭐   │ ⭐⭐⭐   │ Guide   │
└─────────────────────────────┴──────────┴──────────┴─────────┘

Legend:
• Breadth: How many topics covered
• Depth: How detailed each topic is
• Purpose: Best use case
```

---

## 🎓 Learning Objectives

After reading the documentation, you should be able to:

✅ **Understand the architecture**
- Explain the 6-tier architecture
- Describe each layer's responsibility
- Identify dependencies between layers

✅ **Design entities and types**
- Create new entity types
- Define ENUMs
- Create Pydantic models

✅ **Work with builders**
- Use fluent API for entity creation
- Chain methods together
- Generate qualified names

✅ **Use services**
- Create entities via service functions
- Search/query entities
- Manage types

✅ **Handle errors**
- Catch and handle custom exceptions
- Debug issues
- Troubleshoot problems

✅ **Write tests**
- Unit test builders and models
- Integration test services
- Use pytest fixtures

✅ **Extend the system**
- Add new entity types
- Create new services
- Add custom validators

---

## 🔗 Cross-References

### Type System
- Defined in: `ARCHITECTURE_DEEP_DIVE.md` § Type System Architecture
- Reference: `ENTITY_TYPES.md`
- Quick lookup: `ARCHITECTURE_QUICK_REFERENCE.md` § Type Definitions Available

### Service Layer
- Overview: `PROJECT_ARCHITECTURE.md` § Core Components § Service Layer
- Details: `ARCHITECTURE_DEEP_DIVE.md` § Service Layer Design
- Examples: `ARCHITECTURE_QUICK_REFERENCE.md` § Service Function Reference

### Data Models
- Overview: `PROJECT_ARCHITECTURE.md` § Core Components § Metadata Models
- Details: `ARCHITECTURE_DEEP_DIVE.md` § Data Model Architecture
- Guide: `PYDANTIC_MODELS_GUIDE.md`

### Entity Builders
- Overview: `PROJECT_ARCHITECTURE.md` § Core Components § Entity Builders
- Details: `ARCHITECTURE_DEEP_DIVE.md` § Builder Pattern
- Examples: `QUICK_START_ENTITIES.md` § Example Workflow

### Data Flows
- Overview: `PROJECT_ARCHITECTURE.md` § Data Flow
- Sequences: `COMPONENT_INTERACTION_DIAGRAM.md` § Data Flow Interactions
- Lifecycles: `ARCHITECTURE_DEEP_DIVE.md` § Entity Lifecycle

### Error Handling
- Strategy: `ARCHITECTURE_DEEP_DIVE.md` § Error Handling Strategy
- Exception types: `PROJECT_ARCHITECTURE.md` § Exceptions Layer
- Troubleshooting: `ARCHITECTURE_QUICK_REFERENCE.md` § Troubleshooting

---

## 📝 Documentation Meta-Information

### File Sizes (Approximate)
- `ARCHITECTURE_VISUAL_SUMMARY.md`: 400 lines
- `PROJECT_ARCHITECTURE.md`: 600 lines
- `ARCHITECTURE_DEEP_DIVE.md`: 700 lines
- `COMPONENT_INTERACTION_DIAGRAM.md`: 500 lines
- `ARCHITECTURE_QUICK_REFERENCE.md`: 400 lines

### Total Content
- **5 new architecture documents**
- **2500+ lines of documentation**
- **100+ diagrams and tables**
- **200+ code examples**

### Reading Time
- Quick overview: 15-30 minutes
- Complete read: 2-3 hours
- Reference lookup: 5-10 minutes

---

## 🚀 Getting Started

### Step 1: Quick Orientation (5 min)
Open: `ARCHITECTURE_VISUAL_SUMMARY.md`
Read: "Single-Page Architecture Overview" section

### Step 2: Understand the Layers (15 min)
Open: `ARCHITECTURE_QUICK_REFERENCE.md`
Read: "Layer Responsibilities" section

### Step 3: See Code in Action (30 min)
Open: `QUICK_START_ENTITIES.md`
Follow: "Getting Started" section with code

### Step 4: Deep Understanding (1-2 hours)
Read: `PROJECT_ARCHITECTURE.md` then `ARCHITECTURE_DEEP_DIVE.md`

### Step 5: Reference (As needed)
Use: `ARCHITECTURE_QUICK_REFERENCE.md` for lookups

---

## 💡 Pro Tips

1. **Bookmark this index** - You'll come back to it
2. **Read VISUAL_SUMMARY first** - Always start with pictures
3. **Keep QUICK_REFERENCE handy** - Great for copy-paste
4. **Check DEEP_DIVE for patterns** - When designing new features
5. **Use COMPONENT_INTERACTION for flows** - When debugging
6. **Reference ENTITY_TYPES for APIs** - When adding types

---

## 📞 How to Use This Documentation

**For new team members**: Follow Path 1 (Learning the Architecture)

**For implementing features**: Use Path 3 (Specific Task)

**For troubleshooting**: Use Path 4 (Troubleshooting)

**For code reviews**: Reference relevant sections in DEEP_DIVE

**For architecture discussions**: Show VISUAL_SUMMARY

**For onboarding training**: Use QUICK_START + VISUAL_SUMMARY

---

## ✅ Documentation Checklist

Has this documentation helped you with:
- [ ] Understanding the overall architecture
- [ ] Finding specific components
- [ ] Learning design patterns
- [ ] Creating new entities
- [ ] Working with data models
- [ ] Handling errors
- [ ] Writing tests
- [ ] Troubleshooting issues
- [ ] Extending the system
- [ ] Reviewing code

If you checked most boxes ✅, the documentation is working!

---

## 📌 Last Updated

- **Created**: March 30, 2026
- **Last Reviewed**: March 30, 2026
- **Coverage**: Architecture documents (5 files)
- **Status**: Complete and ready for use

---

**Next Step**: Choose your reading path above and dive in! 🚀
