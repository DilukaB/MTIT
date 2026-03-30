from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import uvicorn
from datetime import datetime

app = FastAPI(
    title="Notification Service",
    description="Microservice for managing notifications in the E-Commerce platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# ── Models ──────────────────────────────────────────────────────────────────
class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"

class Notification(BaseModel):
    id: Optional[int] = None
    customer_id: int
    type: NotificationType
    subject: str
    message: str
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: Optional[str] = None
    sent_at: Optional[str] = None

# ── In-memory database ───────────────────────────────────────────────────────
notifications_db: List[Notification] = [
    Notification(
        id=1, customer_id=1, type=NotificationType.EMAIL,
        subject="Order Confirmed",
        message="Your order #1 for Laptop Pro has been confirmed.",
        status=NotificationStatus.SENT,
        created_at="2026-03-01T10:06:00",
        sent_at="2026-03-01T10:06:05"
    ),
    Notification(
        id=2, customer_id=2, type=NotificationType.SMS,
        subject="Payment Pending",
        message="Your payment for order #2 is still pending. Please complete it.",
        status=NotificationStatus.SENT,
        created_at="2026-03-10T14:36:00",
        sent_at="2026-03-10T14:36:03"
    ),
    Notification(
        id=3, customer_id=1, type=NotificationType.PUSH,
        subject="Order Shipped",
        message="Your order #1 has been shipped and is on the way!",
        status=NotificationStatus.PENDING,
        created_at="2026-03-15T09:00:00",
        sent_at=None
    ),
]
counter = 4

# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"service": "Notification Service", "status": "running", "port": 8005}

@app.get("/notifications", response_model=List[Notification], tags=["Notifications"])
def get_all_notifications():
    """Retrieve all notifications"""
    return notifications_db

@app.get("/notifications/{notification_id}", response_model=Notification, tags=["Notifications"])
def get_notification(notification_id: int):
    """Retrieve a specific notification by ID"""
    notif = next((n for n in notifications_db if n.id == notification_id), None)
    if not notif:
        raise HTTPException(status_code=404, detail=f"Notification {notification_id} not found")
    return notif

@app.get("/notifications/customer/{customer_id}", response_model=List[Notification], tags=["Notifications"])
def get_notifications_by_customer(customer_id: int):
    """Retrieve all notifications for a specific customer"""
    return [n for n in notifications_db if n.customer_id == customer_id]

@app.post("/notifications", response_model=Notification, status_code=201, tags=["Notifications"])
def send_notification(notification: Notification):
    """Create and send a new notification"""
    global counter
    notification.id = counter
    counter += 1
    notification.created_at = datetime.now().isoformat()
    # Simulate sending
    notification.status = NotificationStatus.SENT
    notification.sent_at = datetime.now().isoformat()
    notifications_db.append(notification)
    return notification

@app.put("/notifications/{notification_id}/read", response_model=Notification, tags=["Notifications"])
def mark_as_read(notification_id: int):
    """Mark a notification as read"""
    for i, n in enumerate(notifications_db):
        if n.id == notification_id:
            notifications_db[i].status = NotificationStatus.READ
            return notifications_db[i]
    raise HTTPException(status_code=404, detail=f"Notification {notification_id} not found")

@app.put("/notifications/{notification_id}/status", response_model=Notification, tags=["Notifications"])
def update_notification_status(notification_id: int, status: NotificationStatus):
    """Update notification status"""
    for i, n in enumerate(notifications_db):
        if n.id == notification_id:
            notifications_db[i].status = status
            return notifications_db[i]
    raise HTTPException(status_code=404, detail=f"Notification {notification_id} not found")

@app.delete("/notifications/{notification_id}", tags=["Notifications"])
def delete_notification(notification_id: int):
    """Delete a notification by ID"""
    global notifications_db
    notif = next((n for n in notifications_db if n.id == notification_id), None)
    if not notif:
        raise HTTPException(status_code=404, detail=f"Notification {notification_id} not found")
    notifications_db = [n for n in notifications_db if n.id != notification_id]
    return {"message": f"Notification {notification_id} deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
