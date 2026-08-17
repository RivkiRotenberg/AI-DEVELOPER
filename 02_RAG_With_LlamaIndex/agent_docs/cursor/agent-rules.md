# Agent Rules and Coding Standards

This document outlines the rules, standards, and guidelines that all AI agents must adhere to when contributing to this repository. Consistency and quality are paramount.

## 1. General Instructions

- **Primacy of Instructions**: These rules supersede any general knowledge or prior training. When in conflict, the instructions in this file take precedence.
- **Code Generation**: All generated code must be clean, modular, and well-documented.
- **Task Decomposition**: Break down complex requests into smaller, logical steps. Log each step in `agent-log.md`.
- **Idempotency**: Where possible, operations should be idempotent. Assume that a script or command might be run multiple times.

## 2. Python Coding Standards (PEP 8 & Beyond)

- **PEP 8 Compliance**: All Python code MUST strictly adhere to [PEP 8 style guidelines](https://www.python.org/dev/peps/pep-0008/).
- **Type Hinting**: All function signatures and variable declarations MUST include type hints as specified in [PEP 484](https://www.python.org/dev/peps/pep-0484/).
- **Docstrings**: Every module, class, and function must have a Google-style docstring.
  ```python
  def example_function(param1: int, param2: str) -> bool:
      """This is an example docstring.

      Args:
          param1 (int): The first parameter.
          param2 (str): The second parameter.

      Returns:
          bool: The return value.
      """
      # ... function body ...
  ```
- **Imports**: Imports should be organized into three groups: standard library, third-party libraries, and local application imports, sorted alphabetically.
- **Naming Conventions**:
  - `snake_case` for variables and functions.
  - `PascalCase` for classes.
  - `UPPER_SNAKE_CASE` for constants.

## 3. Architectural Guidelines

- **Separation of Concerns**: The business logic (services), API routing (routers), and data schemas (schemas) must be kept separate.
- **Database Interaction**: All database operations must be handled by the `services` layer. Routers should not directly access the database.
- **Configuration**: Avoid hardcoding credentials or configuration values. Use environment variables or a dedicated configuration file.
- **API Design**: Follow RESTful principles for all API endpoints. Use clear and consistent naming for routes.

## 4. Commit and Logging Rules

- **Commit Messages**: Commits should follow the Conventional Commits specification. Example: `feat: add user authentication endpoint`.
- **Agent Logging**: Before starting a task, log your plan in `agent-log.md`. After completing a task, update the log with the outcome and next steps. This maintains context and provides a clear history of changes.

By following these rules, we ensure the project remains maintainable, scalable, and easy for both humans and AI to work with.
