from __future__ import annotations

import os
import re
import time
from enum import Enum
from typing import Optional, Callable, Union, Any, List

import pjsua2 as pj
import yaml
from typing_extensions import TypedDict, Literal

import account
import audio
import ha
import player
import utils
from call_state_change import CallStateChange
from command_client import Command
from command_handler import CommandHandler
from constants import DEFAULT_RING_TIMEOUT, DEFAULT_DTMF_ON, DEFAULT_DTMF_OFF
from log import log


#CallCallback = Callable[[CallStateChange, str, 'Call'], None]
#DtmfMethod = Union[Literal['in_band'], Literal['rfc2833'], Literal['sip_info']]


class WebhookToMsg(TypedDict):
    msg_received: Optional[str]


#class PostActionReturn(TypedDict):
#    action: Literal['return']
#    level: int


#class PostActionJump(TypedDict):
#    action: Literal['jump']
#    menu_id: str


#class PostActionHangup(TypedDict):
#    action: Literal['hangup']


#class PostActionNoop(TypedDict):
#    action: Literal['noop']


#class PostActionRepeatMessage(TypedDict):
#    action: Literal['repeat_message']


#PostAction = Union[PostActionReturn, PostActionJump, PostActionHangup, PostActionNoop, PostActionRepeatMessage]


#class MenuFromStdin(TypedDict):
#    id: Optional[str]
#    message: Optional[str]
#    audio_file: Optional[str]
#    language: Optional[str]
#    action: Optional[Command]
#    choices_are_pin: Optional[bool]
#    post_action: Optional[str]
#    timeout: Optional[int]
#    choices: Optional[dict[Any, MenuFromStdin]]


#class Menu(TypedDict):
#    id: Optional[str]
#    message: Optional[str]
#    audio_file: Optional[str]
#    language: str
#    action: Optional[Command]
#    choices_are_pin: bool
#    post_action: PostAction
#    timeout: float
#    choices: Optional[dict[str, Menu]]
#    default_choice: Optional[Menu]
#    timeout_choice: Optional[Menu]
#    parent_menu: Optional[Menu]


#class CallInfo(TypedDict):
#    local_uri: str
#    remote_uri: str
#    parsed_caller: Optional[str]


#class CallHandling(Enum):
#    LISTEN = 'LISTEN'
#    ACCEPT = 'ACCEPT'

#    @staticmethod
#    def get_or_else(name: Optional[str], default: CallHandling) -> CallHandling:
#        try:
#            return CallHandling[(name or '').upper()]
#        except (KeyError, AttributeError):
#            return default
class Msg(pj.AccountCallback):
    def __init__(self, end_point: pj.Endpoint, sip_account: account.Account, call_id: str, ha_config: ha.HaConfig, webhook_to_msg: Optional[str], webhooks: Optional[WebhookToMsg]):
        pj.AccountCallback.__init__(self, msg, account=None)
        self.msg = msg
        self.end_point = end_point
        self.account = sip_account
        self.ha_config = ha_config
        self.webhook_to_msg = webhook_to_msg
        self.webhooks: WebhookToMsg = webhooks or WebhookToMsg(
            msg_received=None,
        )
        self.callback_id = callback_id
        log(self.account.config.index, 'Registering message with id %s' % self.callback_id)

    def on_pager(self, from_uri, contact, mime_type, body):
        self.msg.on_pager(mime_type, body, account=self.account)

    def trigger_webhook(self, event: ha.WebhookEvent):
        event_id = event.get('event')
        additional_webhook = self.webhooks.get(event_id)
        if additional_webhook:
            log(self.account.config.index, 'Calling additional webhook %s for event %s' % (additional_webhook, event_id))
            ha.trigger_webhook(self.ha_config, event, additional_webhook)
        ha.trigger_webhook(self.ha_config, event)


    def get_callback_id(self) -> str:
        if self.uri_to_call:
            return self.uri_to_call
        call_info = self.get_call_info()
        if call_info['parsed_caller']:
            return call_info['parsed_caller']
        return call_info['remote_uri']
