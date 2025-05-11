from plyer import notification

def notify_user(title="Expense Tracker", message="An update was made to your data."):
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=4
        )
    except Exception as e:
        print("Notification failed:", e)
