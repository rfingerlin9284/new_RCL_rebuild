# Configuration Directory

This directory contains configuration files for the RCL project.

## Guidelines

- **Separation of Concerns**: Keep different types of configuration separate
  - `development.json` or `dev.config.*` for development settings
  - `production.json` or `prod.config.*` for production settings
  - `test.json` or `test.config.*` for test environment settings

- **No Conflicting Logic**: 
  - Use environment-based configuration switching
  - Avoid hard-coded environment checks scattered throughout code
  - Centralize configuration loading and validation

- **Security**:
  - Never commit secrets or API keys
  - Use environment variables for sensitive data
  - Document required configuration in a `.env.example` file

## Structure

Configuration files should be:
- Well-documented with comments
- Validated on load
- Type-safe where possible
