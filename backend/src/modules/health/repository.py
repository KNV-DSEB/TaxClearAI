"""ONLY layer allowed to query the database — see AGENTS.md "Architecture
Rules". Health has no persisted state yet, so this reads from the process
instead; once you have real tables, swap this for a real
`await session.execute(text("SELECT 1"))` check (see src/core/database.py).
"""

import time

_start_time = time.monotonic()


class HealthRepository:
    def get_snapshot(self) -> dict[str, object]:
        return {"status": "ok", "uptime_seconds": int(time.monotonic() - _start_time)}
