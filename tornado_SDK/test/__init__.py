"""
module test
"""
from .voice_translate import VoiceTranslate
from common.create_order_stub import CreateOrderStub
from .level_update import LevelUpdate
from .pay_notice import PayNotice

handlers = {
    "voice_translate": VoiceTranslate,
    "create_order": CreateOrderStub,
    "level_update": LevelUpdate,
    "pay_notice":PayNotice
}


def get_handlers():
    return handlers
