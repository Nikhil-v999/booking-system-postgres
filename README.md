# booking-system-postgres

A booking system for shared, limited resources (think: hostel gym equipment, study rooms, mess slots) where **double-booking is prevented by the database itself** — not by application code checking availability before inserting.

Built to get hands-on with PostgreSQL's advanced features (range types, exclusion constraints, triggers) alongside FastAPI and Docker. This is a learning/portfolio project, not a production system.

## The core idea

Most booking systems prevent overlaps like this:
1. App queries: "is this slot free?"
2. If yes, app inserts the booking.

That has a race condition — two requests can both pass step 1 before either finishes step 2, and you get a double-booking. The usual fix is a lock, a queue, or a retry-on-conflict loop, all bolted on in application code.

This project pushes the guarantee down into the schema instead:

```sql
b_time TSTZRANGE NOT NULL,
b_status TEXT NOT NULL DEFAULT 'active',
EXCLUDE USING gist (b_r_id WITH =, b_time WITH &&) WHERE (b_status = 'active')
```

`b_time` is a `TSTZRANGE` (a time range, not just a timestamp). The `EXCLUDE` constraint tells Postgres: for a given resource (`b_r_id`), no two **active** bookings are allowed to have overlapping (`&&`) time ranges — enforced by a GiST index, at insert time, inside the same transaction. There's no window where two conflicting rows can both exist, even for a moment. If two requests race to book the same slot, Postgres itself rejects the loser with a constraint violation (`23P01`), which the API layer catches and turns into a `409`.

The partial `WHERE (b_status = 'active')` clause means cancelled bookings don't count toward the constraint — so a slot can be rebooked after cancellation without the old row getting in the way.

On top of that, PL/pgSQL triggers handle two things automatically, without the app having to remember to do them:
- Logging every status change to a `status_history` table
- Promoting the next `waitlist` entry to an active booking when a slot is cancelled

## Schema

Four tables: `resources`, `bookings`, `status_history`, `waitlist`. Full schema is in `db/`.

## What it does

- Create resources and check availability for a time slot
- Book a resource — rejected at the DB level if it overlaps an existing active booking
- Cancel a booking — triggers auto-promote the next waitlisted user, if any
- Join a waitlist for a slot that's currently taken
- View a booking's full status history

## What it deliberately doesn't do

No payments, no recurring bookings, no real authentication (plain `user_id`, no login), no admin UI. Out of scope on purpose — the point of this project is the concurrency/data-integrity story, not building a full product.

## Proof: does the constraint actually hold under concurrent load?

Claims about race conditions aren't convincing without actually racing something. Two tests, both run against the live API (not just the DB directly):

**Concurrency test** — two threads fire simultaneous `POST /bookings` for the same resource and time slot, released at the same instant via a `threading.Barrier`:

```
thread-2  200  {'b_id': 13, ...}
thread-1  409  {'detail': 'Booking conflicts with an existing active booking'}
```

One booking succeeds, one is rejected, and the DB confirms only a single active row exists for that slot afterward. No double-booking, even when both requests hit at the same moment.

**Cancel–rebook test** — repeatedly cancel and rebook the same slot (mixing same and different users) via the live API (Swagger UI) to confirm the partial `EXCLUDE` correctly ignores cancelled rows instead of permanently blocking the slot:

```
b_id 9  -> cancelled
b_id 16 -> cancelled
b_id 17 -> cancelled
b_id 18 -> active
```

Only one active row ever existed for the slot across the whole cycle.

Concurrency test script: `scripts/concurrency_test.py` (cancel–rebook was run manually through Swagger UI, not scripted)

## Tech stack

FastAPI, PostgreSQL, SQLAlchemy, Docker + Docker Compose, psycopg2

## Future work

- **LISTEN/NOTIFY** — have the waitlist-promotion trigger emit a Postgres `NOTIFY`, and expose a WebSocket/SSE endpoint so a promoted user is pushed a real-time update instead of having to poll for it. Not implemented yet.