from django.dispatch import Signal

## Our signals

# recurring subscriptions
subscribed = Signal(providing_args=["payment"])
unsubscribed = Signal(providing_args=["payment"])
paid = Signal(providing_args=["payment"])

# upgrade/downgrade possibility check
change_check = Signal()
