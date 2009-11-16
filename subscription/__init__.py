### -*- coding: utf-8 -*- ##

from django.db.models.signals import post_delete 

import paypalhandlers
import signals
from models import Transaction, UserSubscription

def deleted(instance, **kwargs):
    Transaction(user=instance.user, subscription=instance.subscription, 
                event=Transaction.EVENT_REMOVED).save()
post_delete.connect(deleted, sender=UserSubscription)

def cancelled(sender, **kwargs): 
    Transaction(user=sender.user, subscription=sender.subscription,
                event=Transaction.EVENT_CANCELLED
                ).save()
signals.cancelled.connect(cancelled, sender=UserSubscription)

def activated(sender, **kwargs):
    Transaction(user=sender.user, subscription=sender.subscription,
                event=Transaction.EVENT_ACTIVATED
                ).save()
signals.activated.connect(activated, sender=UserSubscription)

def paid(payment, sender, **kwargs):
    Transaction(user=sender.user, subscription=sender.subscription, ipn=payment,
                event=Transaction.EVENT_PAYMENT, amount=payment.mc_gross
                ).save()
signals.paid.connect(paid, sender=UserSubscription)

def subscribed(sender, **kwargs):
    Transaction(user=sender.user, subscription=sender.subscription,
                event=Transaction.EVENT_SUBSCRIBED
                ).save()
signals.subscribed.connect(subscribed, sender=UserSubscription)

def recured(sender, **kwargs):
    Transaction(user=sender.user, subscription=sender.subscription,
                event=Transaction.EVENT_RECURED
                ).save()
signals.recured.connect(recured, sender=UserSubscription)
