from app.repositories.order import (
    get_order_by_id,
    get_order_items,
    get_order_status_history
)

def track_order(order_id):
    order = get_order_by_id(order_id)
    items = get_order_items(order_id)
    history = get_order_status_history(order_id)

    return {
        "order": order,
        "items": items,
        "status_history": history
    }