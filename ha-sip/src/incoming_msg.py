from typing import Optional

from typing_extensions import TypedDict

import msg


class IncomingMsgConfig(TypedDict):
    allowed_numbers: Optional[list[str]]
    blocked_numbers: Optional[list[str]]
    answer_after: Optional[int]
    webhook_to_msg: Optional[call.WebhookToMsg]
