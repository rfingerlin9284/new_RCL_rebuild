# RCL Rebuild - Rick Clean Live

A clean, well-organized rebuild of the Rick Clean Live (RCL) project with proper separation of concerns.

## Project Structure

```
new_RCL_rebuild/
├── src/              # Source code
├── tests/            # Test files
├── docs/             # Documentation
├── config/           # Configuration files
├── LICENSE           # MIT License
└── README.md         # This file
```

## Design Principles

This rebuild follows strict guidelines to prevent common code quality issues:

### 1. **No Ghost Code**
- Removed all commented-out code blocks
- Use version control (git) for code history instead of comments
- Delete unused code rather than commenting it out

### 2. **No Embedded Prompts**
- Documentation is in the `docs/` directory
- No TODO comments without associated issues/tickets
- Clear, purposeful comments only when necessary

### 3. **Separated Logic**
- Clear separation between:
  - Business logic (`src/`)
  - Configuration (`config/`)
  - Tests (`tests/`)
  - Documentation (`docs/`)
- No conflicting conditional logic or feature gates without proper abstraction

### 4. **Clean Extraction**
- Reusable components are properly extracted into modules
- Single Responsibility Principle for all files
- Clear, descriptive naming conventions

## Getting Started

1. Clone the repository
2. Review the structure guidelines in each directory's README
3. Follow the coding standards in CONTRIBUTING.md
4. Keep the codebase clean and organized

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on maintaining code quality and structure.
