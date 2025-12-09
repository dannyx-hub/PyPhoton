import platform

def register(engine):
    system = platform.system()

    icon_path = None

    if system == "Darwin":
        import pync
        def notify(title, message):
            pync.notify(
                message,
                title=title,
                appIcon=icon_path,
                activate="com.apple.Terminal"
            )
    else:
        from plyer import notification
        def notify(title, message):
            notification.notify(
                title=title,
                message=message,
                app_name="PyPhoton",
                app_icon=icon_path,
                timeout=5
            )

    engine.notifications = notify
    print("[Notifications] Plugin ready")
