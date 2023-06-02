from typing import Any


"""
_EVENT_MAP: Dict
_EVENT_MAP[Element]: 
    key: string,
    value:
        title: string
        content: string
        icon: string

Example: 
_EVENT_MAP = {
    'test': {
        'title': 'Test',
        'content': 'Test notification',
        'icon': 'https://png.pngtree.com/test.png'
    }
}
"""

_EVENT_MAP = dict()


def create_notification(event_key: str, entity: Any, params: list = None):
    event = _EVENT_MAP.get(event_key)

    if not params:
        params = []

    if event:
        event['content'] = event['content'].format(*params)

        """Custom handler"""
