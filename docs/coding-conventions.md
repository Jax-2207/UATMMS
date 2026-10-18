# UATMMS Coding & Development Conventions

## 1. Python & FastAPI Backend
* **Python Version**: 3.11+ (running 3.13 in current environment).
* **Type Hints**: Mandatory for all function signatures, return types, and class attributes.
* **Data Validation**: Use **Pydantic v2** models for all API requests, responses, and internal event schemas.
* **Explicit Units**: Variable names must include physical units:
  * Distances: `length_m`, `position_m`
  * Speeds: `speed_mps`, `speed_limit_kph`
  * Times: `travel_time_s`, `waiting_time_s`, `timestamp_epoch_ms`
  * Flow: `flow_veh_per_hr`
* **Error Handling**: Throw domain-specific exceptions inheriting from `UATMMSError` (in `core/errors.py`), which are caught and converted to standard RFC 7807 problem details HTTP responses.
* **Logging**: Use Python's `logging` or `loguru` with structured formatting including timestamp, module, level, and context (`run_id`, `junction_id`).

## 2. Frontend (React + TypeScript)
* **Language**: TypeScript with strict mode enabled (`noImplicitAny: true`).
* **Styling**: Tailwind CSS with custom design tokens for traffic visualization (green, amber, red, emergency sirens, night mode slate palette).
* **Components**: Clean atomic components with clear prop interfaces.
* **State Management**: React state hooks with Context or lightweight state store for simulation state; WebSocket hook with automatic reconnection.
* **Component Testing**: Accessible semantic elements with unique `data-testid` or `id` attributes for automated browser testing.

## 3. Git & Repository Management
* **Branching Model**: Trunk-based or feature-branch workflow (`feat/*`, `fix/*`, `experiment/*`).
* **Commit Messages**: Conventional Commits format (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `perf:`).
* **Secrets & Artifacts**: Never commit `.env`, `*.pt`, `*.zip`, or database credentials to Git. Use `.gitignore`.
