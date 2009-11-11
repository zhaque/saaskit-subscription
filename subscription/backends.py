### -*- coding: utf-8 -*- ##

from django.contrib.auth.backends import ModelBackend

from subscription.models import UserSubscription

class UserSubscriptionBackend(ModelBackend):
    """
        This backend gets permissions from current user subscription.
    """
    def get_all_permissions(self, user_obj):
        perm_cache = super(UserSubscriptionBackend, self).get_all_permissions(user_obj)
        if user_obj.subscription.active:
            try:
                perm_cache.update(set([u"%s.%s" % (p.content_type.app_label, p.codename) 
                            for p in user_obj.subscription.subscription.permissions.select_related()]))
            except UserSubscription.DoesNotExist:
                pass
        return perm_cache
