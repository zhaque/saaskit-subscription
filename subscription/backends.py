### -*- coding: utf-8 -*- ##

from django.contrib.auth.backends import ModelBackend

from subscription.models import UserSubscription

class UserSubscriptionBackend(ModelBackend):
    """
        This backend gets permissions from current user subscription.
    """
    def get_all_permissions(self, user_obj):
        perm_cache = super(UserSubscriptionBackend, self).get_all_permissions(user_obj)
        try:
            us = user_obj.subscription
        except UserSubscription.DoesNotExist:
            pass
        else:
            perm_cache.update(set([u"%s.%s" % (p.content_type.app_label, p.codename) 
                                   for p in us.subscription.permissions.select_related()]))
        
        return perm_cache
