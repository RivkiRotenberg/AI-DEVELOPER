# System Insights by Claude Code

This document outlines key technical constraints, design guidelines, and API challenges discovered during the development of the project. These insights are intended to guide future development and ensure consistency.

## 1. Technical Constraints

- **Database**: The current implementation uses an in-memory dictionary (`mock_db.py`) for simplicity. This is not suitable for production and must be replaced with a persistent database like PostgreSQL or SQLite.
- **Authentication**: No authentication or authorization layer is currently implemented. All endpoints are public. This is a major security risk and must be addressed before deployment.
- **Scalability**: The application runs as a single server process. It will not scale to handle high traffic loads without a proper load balancing and multi-process architecture.

## 2. RTL Design Guidelines

- **Layout Direction**: All UI components must be designed to support Right-to-Left (RTL) layouts for languages like Hebrew and Arabic. Use CSS Flexbox or Grid with logical properties (e.g., `margin-inline-start` instead of `margin-left`).
- **Text Alignment**: Ensure all text is properly aligned for RTL languages. Titles, labels, and other text elements should be right-aligned.
- **Component Flipping**: Icons, buttons with directional arrows, and other asymmetrical UI elements must be flipped horizontally in RTL mode.

## 3. API Challenges & Solutions

- **Challenge**: Lack of a clear and consistent API schema.
  - **Solution**: Implemented Pydantic models in `schemas/` to define strict data contracts for API requests and responses. This ensures type safety and clear documentation.

- **Challenge**: Difficulty in managing application state and dependencies.
  - **Solution**: Introduced a mock service layer (`services/`) to decouple business logic from the API endpoints. This makes the code more modular and easier to test.

- **Challenge**: No real-time updates in the frontend when data changes in the backend.
  - **Solution**: The Gradio UI uses a polling mechanism (`gr.DataFrame(value=get_tasks_df, every=5)`) to refresh the task list periodically. For a better user experience, this should be replaced with WebSockets or Server-Sent Events (SSE) for real-time updates.
