
from django.contrib.auth.models import User
from django.db.models.signals import post_save

#import paypalhandlers
from models import UserSubscription, Subscription

def free_subscribe(instance, created, **kwargs):
    """
        Every user must have a free subscription
        We consider here to get plan with id equal to 1. We install it with fixtures
    """

    if created:
        free = Subscription.objects.get(id=1)
        UserSubscription(user=instance, subscription=free).save()
        
post_save.connect(free_subscribe, sender=User)
