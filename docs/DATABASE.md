# Database Schema

Pablo uses PostgreSQL with SQLAlchemy ORM. Schema defined in `src/models.py`, migrations managed by Alembic.

---

## Entity Relationship Overview

```
people ──< task_opt_outs >── task_types
  │                               │
  │                           task_instances ──< weeks
  │                               │
  └──< completion_log ────────────┘
  │
  └──< penalties >── weeks
```

---

## Tables

### `people`
Corridor residents registered via `/start`.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto |
| `telegram_id` | BIGINT UNIQUE | Telegram user ID |
| `name` | VARCHAR(100) | Telegram first name |
| `username` | VARCHAR(100) | Telegram @username (nullable) |
| `joined_date` | DATE | Registration date |
| `active` | BOOLEAN | Default `true` |

---

### `task_types`
The 22 predefined cleaning task definitions.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto |
| `name` | VARCHAR(100) UNIQUE | e.g. `"Toilet 1"` |
| `category` | VARCHAR(50) | `toilet`, `shower`, `kitchen`, `fridge`, `hallway`, `laundry`, `trash`, `other` |
| `description` | TEXT | Short description |
| `instructions` | TEXT | Step-by-step how-to |
| `media_file_id` | VARCHAR(200) | Telegram file_id for photo |
| `frequency` | VARCHAR(20) | Default `"weekly"` |
| `estimated_duration_minutes` | INTEGER | |
| `location` | VARCHAR(255) | Physical location |

---

### `task_opt_outs`
Which people are permanently exempt from which task types.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `person_id` | FK → people | CASCADE delete |
| `task_type_id` | FK → task_types | CASCADE delete |
| `reason` | VARCHAR(200) | Required explanation |
| `created_at` | DATETIME | |

Unique constraint on `(person_id, task_type_id)`.

---

### `weeks`
Weekly cleaning cycles.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `year` | INTEGER | ISO year |
| `week_number` | INTEGER | ISO week number |
| `start_date` | DATE | Monday of the week |
| `deadline` | DATETIME | Sunday 23:58 by default |
| `closed` | BOOLEAN | `false` = active |

Unique constraint on `(year, week_number)`.

---

### `task_instances`
One row per task per week. The "to-do list" for each cycle.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `week_id` | FK → weeks | CASCADE delete |
| `task_type_id` | FK → task_types | CASCADE delete |
| `status` | VARCHAR(20) | `pending`, `completed`, `skipped` |
| `completed_by` | FK → people | Nullable |
| `completed_at` | DATETIME | Nullable |
| `notes` | TEXT | Nullable |

Unique constraint on `(week_id, task_type_id)`.

---

### `completion_log`
Full audit trail of all task actions.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `task_instance_id` | FK → task_instances | CASCADE delete |
| `person_id` | FK → people | SET NULL on delete |
| `action` | VARCHAR(20) | `completed`, `amended` |
| `timestamp` | DATETIME | Auto |
| `message_id` | BIGINT | Telegram message ID |

---

### `penalties`
Reserved for future penalty tracking. Not yet used in bot logic.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `person_id` | FK → people | CASCADE delete |
| `week_id` | FK → weeks | CASCADE delete |
| `amount_eur` | NUMERIC(5,2) | Penalty in euros |
| `penalty_type` | VARCHAR(50) | `missed_task`, `late_completion` |
| `paid` | BOOLEAN | Default `false` |
| `paid_at` | DATETIME | Nullable |
| `paid_via` | VARCHAR(50) | `money`, `cooking`, `transferred` |

---

## Common Queries

### Current active week
```python
from src.database import get_db
from src.models import Week

with get_db() as db:
    week = db.query(Week).filter_by(closed=False).order_by(Week.deadline.desc()).first()
```

### Pending tasks this week
```python
from src.models import TaskInstance

with get_db() as db:
    pending = db.query(TaskInstance).filter_by(
        week_id=week.id, status="pending"
    ).all()
```

### Person's completions this week
```python
completed = db.query(TaskInstance).filter_by(
    week_id=week.id, completed_by=person.id
).count()
```

---

## Migrations

Alembic is configured and ready. Use it for any schema changes:

```bash
# Create a migration after model changes
uv run alembic revision --autogenerate -m "add column X"

# Apply pending migrations
uv run alembic upgrade head

# Rollback one step
uv run alembic downgrade -1

# See migration history
uv run alembic history
```

Migration files live in `alembic/versions/` (auto-generated, committed to git).
