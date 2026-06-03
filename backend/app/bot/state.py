from __future__ import annotations

from enum import IntEnum


class BotState(IntEnum):
    WAITING_URL_OR_MANUAL = 0
    WAITING_MANUAL_FIELDS = 1
    WAITING_CONFIRMATION = 2
    EDITING_FIELD = 3
    GENERATING_CONTENT = 4
    WAITING_IMAGE_CHOICE = 5
    WAITING_POST_ACTION = 6
