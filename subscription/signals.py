### -*- coding: utf-8 -*- ####################################################
""" subscription signals """
from django.dispatch import Signal


# recurring subscriptions
subscribed = Signal()
paid = Signal(providing_args=["payment"])
cancelled = Signal()
activated = Signal()
recured = Signal()

# upgrade/downgrade possibility check
change_check = Signal()
