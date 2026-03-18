"""Generic event scheduler primitives for the IMS Python port.

This module only provides deterministic, technical event ordering.
It intentionally does not contain IMS-specific entities or rules.
"""

from dataclasses import dataclass, field
import heapq
from typing import Any


@dataclass(order=True, slots=True)
class Event:
    """Generic scheduled event with explicit, stable ordering keys."""

    period: int
    logtime: int
    priority: int
    sequence: int
    name: str = field(compare=False, default="event")
    payload: Any = field(compare=False, default=None)


class Scheduler:
    """Priority-queue based scheduler with stable event ordering."""

    def __init__(self) -> None:
        self._queue: list[Event] = []
        self._sequence = 0

    def plan(
        self,
        *,
        period: int,
        logtime: int,
        priority: int = 0,
        name: str = "event",
        payload: Any = None,
    ) -> Event:
        """Schedule a new event.

        Events are ordered explicitly by period, logtime, priority and a final
        monotonically increasing sequence number for stable tie-breaking.
        """

        event = Event(
            period=period,
            logtime=logtime,
            priority=priority,
            sequence=self._sequence,
            name=name,
            payload=payload,
        )
        self._sequence += 1
        heapq.heappush(self._queue, event)
        return event

    def pop(self) -> Event:
        """Return the next event from the scheduler queue."""

        return heapq.heappop(self._queue)

    def empty(self) -> bool:
        """Return ``True`` when no events are scheduled."""

        return not self._queue
