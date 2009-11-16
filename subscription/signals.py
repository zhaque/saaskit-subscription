from django.dispatch import Signal

## Our signals

# recurring subscriptions
subscribed = Signal()
paid = Signal(providing_args=["payment"])
cancelled = Signal()
activated = Signal()
recured = Signal()

# upgrade/downgrade possibility check
change_check = Signal()
