### -*- coding: utf-8 -*- ####################################################
""" Handle PayPal signals """

from django.contrib.auth.models import User

from paypal.standard import ipn

from subscription.models import Transaction, Subscription
import signals

def _ipn_usersubscription(payment):
    try:
        user_id = int(payment.custom)
    except ValueError:
        u = None
    else:
        try: u = User.objects.get(id=user_id)
        except User.DoesNotExist: u = None

    if u and s:
        try: us = UserSubscription.objects.get(subscription=s, user=u)
        except UserSubscription.DoesNotExist:
            us = UserSubscription(user=u, subscription=s, active=False)
            Transaction(user=u, subscription=s, ipn=payment,
                        event=Transaction.EVENT_NEW, amount=payment.mc_gross
                        ).save()
        return us
    

def handle_payment_was_successful(sender, **kwargs):
    us = _ipn_usersubscription(sender)
    if us:
        u, s = us.user, us.subscription
        if sender.mc_gross == s.price:
            us.extend()
            us.save()
            Transaction(user=u, subscription=s, ipn=sender,
                        event=Transaction.EVENT_PAYMENT, amount=sender.mc_gross
                        ).save()
            signals.paid.send(s, ipn=sender, subscription=s, user=u,
                              usersubscription=us)
        else:
            Transaction(user=u, subscription=s, ipn=sender,
                        event=Transaction.EVENT_PAYMENT_INCORRECT, amount=sender.mc_gross
                        ).save()
            signals.event.send(s, ipn=sender, subscription=s, user=u,
                               usersubscription=us, event='incorrect payment')
ipn.signals.payment_was_successful.connect(handle_payment_was_successful)

def handle_payment_was_flagged(sender, **kwargs):
    us = _ipn_usersubscription(sender)
    if us:
        u, s = us.user, us.subscription
        Transaction(user=u, subscription=s, ipn=sender,
                    event=Transaction.EVENT_PAYMENT_FLAGGED, amount=sender.mc_gross
                    ).save()
        signals.event.send(s, ipn=sender, subscription=s, user=u, event='flagged')
ipn.signals.payment_was_flagged.connect(handle_payment_was_flagged)

def handle_subscription_cancel(sender, **kwargs):
    us = _ipn_usersubscription(sender)
    if us:
        u, s = us.user, us.subscription
        us.active = False
        Transaction(user=u, subscription=s, ipn=sender,
                    event=Transaction.EVENT_DEACTIVATED, amount=sender.mc_gross
                    ).save()
                    
        signals.unsubscribed.send(s, ipn=sender, subscription=s, user=u,
                                  usersubscription=us,
                                  reason='cancel')
    
ipn.signals.subscription_cancel.connect(handle_subscription_cancel)
ipn.signals.subscription_eot.connect(handle_subscription_cancel)

def handle_subscription_signup(sender, **kwargs):
    us = _ipn_usersubscription(sender)
    u, s = us.user, us.subscription
    if us:
        # delete all user's other subscriptions
        for old_us in u.usersubscription_set.exclude(id__exact=us.id):
            old_us.delete()
            
            Transaction(user=u, subscription=s, ipn=sender,
                        event=Transaction.EVENT_REMOVED, amount=sender.mc_gross
                        ).save()

        # activate new subscription
        us.active = True
        us.save()
        Transaction(user=u, subscription=s, ipn=sender,
                    event=Transaction.EVENT_ACTIVATED, amount=sender.mc_gross
                    ).save()

        signals.subscribed.send(s, ipn=sender, subscription=s, user=u,
                                usersubscription=us)
ipn.signals.subscription_signup.connect(handle_subscription_signup)

def handle_subscription_modify(sender, **kwargs):
    us = _ipn_usersubscription(sender)
    u, s = us.user, us.subscription
    
    if us:
        # delete all user's other subscriptions
        for old_us in u.usersubscription_set.all():
            if old_us == us: continue     # don't touch current subscription
            
            #old_us.delete()
            old_us.active = False
            Transaction(user=u, subscription=s, ipn=sender,
                        event='remove subscription (deactivated)', amount=sender.mc_gross
                        ).save()

        # activate new subscription
        us.active = True
        us.save()
        Transaction(user=u, subscription=s, ipn=sender,
                    event=Transaction.EVENT_ACTIVATED, amount=sender.mc_gross
                    ).save()

        signals.subscribed.send(s, ipn=sender, subscription=s, user=u,
                                usersubscription=us)

ipn.signals.subscription_modify.connect(handle_subscription_modify)
