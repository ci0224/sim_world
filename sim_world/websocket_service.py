from typing import Any, List, Literal
from fastapi import WebSocket

# Store WebSocket clients
clients: List[WebSocket] = []


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
