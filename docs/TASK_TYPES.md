# Task Types

All 22 cleaning tasks pre-loaded by `scripts/populate_db.py`.

---

## Categories & Amounts Per Week

| Category | Emoji | Tasks/week | Tasks included |
|---|---|---|---|
| Toilet | 🚽 | 2 | Toilet 1, 2, 3, 4 (2 assigned/week) |
| Shower | 🚿 | 2 | Shower A, B, C, D (2 assigned/week) |
| Kitchen | 🍳 | 3 | Kitchen A, E, I |
| Fridge | ❄️ | 2 | Fridge 1, 2, 3, 4 (2 assigned/week) |
| Hallway | 🚪 | 1 | Hallway Main, Hallway Side |
| Laundry | 🧺 | 1 | Wash Room |
| Trash | 🗑️ | 2 | Paper, Glass, Plastic, Kitchen Trash |
| Other | 📦 | 1 | (as needed) |

> The `CATEGORY_AMOUNTS` dict in `src/menus.py` controls how many instances are tracked per category per week.

---

## Full Task List

### 🚽 Toilets (4 types)

| Name | Location | Duration |
|---|---|---|
| Toilet 1 | 1st floor | 15 min |
| Toilet 2 | 2nd floor | 15 min |
| Toilet 3 | 3rd floor | 15 min |
| Toilet 4 | 4th floor | 15 min |

**Instructions:** Clean toilet bowl, wipe seat and lid, wipe outside of toilet, clean sink and mirror, mop floor, replace paper roll if needed.

### 🚿 Showers (4 types)

| Name | Location | Duration |
|---|---|---|
| Shower A | East wing | 15 min |
| Shower B | West wing | 15 min |
| Shower C | North side | 15 min |
| Shower D | South side | 15 min |

**Instructions:** Scrub tiles, clean drain, wipe glass/curtain, clean shelf, mop floor.

### 🍳 Kitchen (3 types)

| Name | Area | Duration |
|---|---|---|
| Kitchen A | Stovetop & counters | 20 min |
| Kitchen E | Oven & microwave | 20 min |
| Kitchen I | Sink & dishwasher area | 15 min |

**Instructions:** Wipe all surfaces, clean appliances, take out trash if full, leave surfaces clear.

### ❄️ Fridges (4 types)

| Name | Location | Duration |
|---|---|---|
| Fridge 1 | Kitchen left | 10 min |
| Fridge 2 | Kitchen right | 10 min |
| Fridge 3 | Common room | 10 min |
| Fridge 4 | Storage area | 10 min |

**Instructions:** Remove expired items, wipe shelves and door seals, check for spills.

> People with private fridges can opt out of communal fridge tasks — see `/optout`.

### 🚪 Hallways (2 types)

| Name | Location | Duration |
|---|---|---|
| Hallway Main | Main corridor | 20 min |
| Hallway Side | Side corridor | 15 min |

**Instructions:** Sweep and mop the floor, wipe light switches and door handles, remove any items left in the corridor.

### 🧺 Laundry (1 type)

| Name | Location | Duration |
|---|---|---|
| Wash Room | Basement | 15 min |

**Instructions:** Wipe washer and dryer tops, clean lint trap, sweep floor, remove forgotten laundry to lost-and-found shelf.

### 🗑️ Trash (4 types)

| Name | Container | Duration |
|---|---|---|
| Trash Paper | Paper bin | 5 min |
| Trash Glass | Glass bin | 5 min |
| Trash Plastic | Plastic bin | 5 min |
| Trash Kitchen | Kitchen bin | 5 min |

**Instructions:** Take the full bag to the appropriate external container, replace with a new bag, wipe down the bin if needed.

---

## Adding a New Task Type

Via Python:
```python
from src.database import get_db
from src.models import TaskType

with get_db() as db:
    new_task = TaskType(
        name="Balcony",
        category="other",
        description="Clean the shared balcony",
        instructions="1. Sweep floor\n2. Wipe railings\n3. Empty ashtray if present",
        estimated_duration_minutes=15,
        location="3rd floor balcony"
    )
    db.add(new_task)
    db.commit()
```

After adding, re-run `scripts/populate_db.py` or add the task manually. New tasks will appear in the next week's task instance generation.

---

## Adding an Opt-Out

Via Python (for admins):
```python
from src.models import Person, TaskType, TaskOptOut

with get_db() as db:
    person = db.query(Person).filter_by(telegram_id=123456789).first()
    task = db.query(TaskType).filter_by(name="Fridge 1").first()
    opt_out = TaskOptOut(
        person_id=person.id,
        task_type_id=task.id,
        reason="Has private fridge in room"
    )
    db.add(opt_out)
    db.commit()
```

Via bot (self-service):
```
/optout Fridge 1 I have my own fridge
```
