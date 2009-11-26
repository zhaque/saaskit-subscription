### -*- coding: utf-8 -*- ####################################################
""" add different types of transaction """

from django.db.models.signals import post_delete, post_save

from subscription import signals
from subscription.models import Transaction, UserSubscription

def subscription_deleted(instance, **kwargs):
    Transaction(user=instance.user, subscription=instance.subscription, 
                event=Transaction.EVENT_REMOVED).save()
post_delete.connect(subscription_deleted, sender=UserSubscription)

def subscription_cancelled(sender, **kwargs): 
    Transaction(user=sender.user, subscription=sender.subscription,
                event=Transaction.EVENT_CANCELLED
                ).save()
signals.cancelled.connect(subscription_cancelled)

def subscription_activated(sender, **kwargs):
    Transaction(user=sender.user, subscription=sender.subscription,
                event=Transaction.EVENT_ACTIVATED
                ).save()
signals.activated.connect(subscription_activated)

def subscription_paid(payment, sender, **kwargs):
    Transaction(user=sender.user, subscription=sender.subscription, ipn=payment,
                event=Transaction.EVENT_PAYMENT, amount=payment.mc_gross
                ).save()
signals.paid.connect(subscription_paid)

def subscribedormodified(sender, **kwargs):
    Transaction(user=sender.user, subscription=sender.subscription,
                event=Transaction.EVENT_SUBSCRIBED
                ).save()
signals.subscribed.connect(subscribedormodified)

def subscription_created(instance, created, **kwargs):
    if created:
        Transaction(user=instance.user, subscription=instance.subscription,
                    event=Transaction.EVENT_SUBSCRIBED
                    ).save()
post_save.connect(subscription_created, sender=UserSubscription)

def subscription_recured(sender, **kwargs):
    Transaction(user=sender.user, subscription=sender.subscription,
                event=Transaction.EVENT_RECURED
                ).save()
signals.recured.connect(subscription_recured)
