import asyncio
from typing import Any, List, Literal
from fastapi import WebSocket

# Store WebSocket clients
clients: List[WebSocket] = []


def notify_update_in_background(
    updated_type: Literal["World", "Character", "Event"],
    updated_id: str,
    updated_value: Any,
):
    task = asyncio.create_task(notifyUpdate(updated_type, updated_id, updated_value))

    def done_callback(future):
        try:
            result = future.result()
            print("Task completed:", result)
        except Exception as e:
            print("Task failed:", e)

    task.add_done_callback(done_callback)


async def notifyUpdate(
    updated_type: Literal["World", "Character", "Event"],
    updated_id: str,
    updated_value: Any,
) -> None:
    """
    Notify all connected WebSocket clients about an update.

    Args:
        updated_type: Type of the updated entity
        updated_id: ID of the updated entity
        updated_value: New value/state of the entity
    """
    message = {
        "event": "update",
        "updated_type": updated_type,
        "updated_id": updated_id,
        "updated_value": updated_value,
    }
    for client in clients:
        await client.send_json(message)
