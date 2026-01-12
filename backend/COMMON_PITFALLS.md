# Common Pitfalls & Breakage Points

This document outlines standard issues encountered with the specific models in this project and how to avoid them.

## 1. user_id vs UUIDs
- **The Issue**: We use `String` for IDs in `models.py` for SQLite compatibility, but often Pydantic schemas expect `UUID` types.
- **Breakage**: Pydantic validation errors (`value is not a valid uuid`) when the frontend sends a string that isn't a valid UUID format, or when the DB returns a string and Pydantic strictly wants a UUID object.
- **Fix**: Ensure schemas use `str` for IDs, or use `pydantic.UUID4` and handle the string conversion explicitly in the CRUD layer.

## 2. MasterUser & BusinessUser (Circular & Relations)
- **The Issue**: No explicit relationship (Foreign Key) is defined in the ORM for `parent_reseller_id`.
- **Breakage**: `db.query(MasterUser).filter(...)` won't automatically fetch children. You must manually query `BusinessUser` by `parent_reseller_id`.
- **Constraint Violation**: If you delete a Reseller, the Business Users become orphans. Manual `ON DELETE CASCADE` logic is required in the application layer.

## 3. CreditTransaction (Atomic Integer Math)
- **The Issue**: Using `Float` for currency/credits.
- **Breakage**: Floating point errors (e.g., `100.0 - 0.1 = 99.90000000001`).
- **Fix**: In production, use `Decimal` or `Integer` (cents). For now, round heavily or accept micro-discrepancies.
- **Race Condition**: If two requests hit `distribute_credits` simultaneously for the same reseller, they might both read the same `available_credits` and overwrite each other.
- **Fix**: Use `db.query(...).with_for_update()` (Postgres) or optimistic locking (version column). SQLite locks the whole file so it's safer locally, but dangerous in prod.

## 4. Message & UsageLog (Double Imports)
- **The Issue**: `models.py` imports `database` and `main.py` imports `models`. If logic is moved to `services/`, circular imports often happen between `services` and `models` if typing hints aren't quoted.
- **Breakage**: `ImportError: cannot import name 'User' from partially initialized module`.
- **Fix**: Put all Business Logic in `services/`, all DB Schemas in `models/`, all Pydantic Schemas in `schemas/`. Never let `models` import `services`.

## 5. LinkedDevice & Sessions
- **The Issue**: Expiry logic is often checked only on "read".
- **Breakage**: The DB fills up with millions of expired sessions.
- **Fix**: Need a background job (Celery/Cron) to `DELETE FROM device_sessions WHERE expires_at < NOW()`.

## 6. WhatsAppOfficialConfig (Encryption)
- **The Issue**: `access_token` is stored as plain text.
- **Breakage**: Security audit failure. If the DB is leaked, all WhatsApp accounts are compromised.
- **Fix**: Encrypt this column using a symmetric key (e.g., Fernet) before writing to DB.

