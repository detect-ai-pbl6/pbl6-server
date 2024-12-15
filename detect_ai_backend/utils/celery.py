from typing import Any, Dict

import msgpack

from detect_ai_backend.celery import app as current_app


def publish_message_to_group(message: Dict[str, Any], group: str) -> None:
    with current_app.producer_pool.acquire(block=True) as producer:
        producer.publish(
            msgpack.packb(
                {
                    "__asgi_group__": group,
                    **message,
                }
            ),
            exchange="groups",  # groups_exchange
            content_encoding="binary",
            routing_key=group,
            retry=False,  # Channel Layer at-most once semantics
        )
