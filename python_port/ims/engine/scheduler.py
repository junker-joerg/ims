class Scheduler:
    """
    Minimaler Platzhalter für den künftigen Scheduler.

    In diesem PR wird noch keine echte Ereignislogik implementiert.
    Ziel ist nur ein stabiles Import-Grundgerüst.
    """

    def __init__(self) -> None:
        self._events: list[object] = []

    def empty(self) -> bool:
        return len(self._events) == 0
