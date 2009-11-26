
from datetime import datetime

from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.utils.html import conditional_escape as esc
from django.contrib.auth.admin import UserAdmin, User
from django.db import models

from saaskit.widgets.readonlyhidden import ReadOnlyWidgetWithHidden
from subscription.models import Subscription, UserSubscription, Transaction

def _pricing(sub): return sub.get_pricing_display()
def _trial(sub): return sub.get_trial_display()

def _subscription(trans):
    return u'<a href="/admin/subscription/subscription/%d/">%s</a>' % (
        trans.subscription.pk, esc(trans.subscription) )
_subscription.allow_tags = True

def _user(trans):
    return u'<a href="/admin/auth/user/%d/">%s</a>' % (
        trans.user.pk, esc(trans.user) )
_user.allow_tags = True

def _ipn(trans):
    return u'<a href="/admin/ipn/paypalipn/%d/">#%s</a>' % (
        trans.ipn.pk, trans.ipn.pk )
_ipn.allow_tags = True

def event(trans): return trans.get_event_display()
def timestamp(trans): return trans.timestamp

class InlineBase(admin.TabularInline):
    extra = 0
    
    def get_formset(self, request, obj=None, **kwargs):
        kwargs['can_delete'] = False
        return super(InlineBase, self).get_formset(request, obj=obj, **kwargs)
    
    
class TransactionInline(InlineBase):
    model = Transaction

class UserSubscriptionInline(InlineBase):
    model = UserSubscription
    
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', _pricing, _trial)
    filter_horizontal = ('permissions',)
    inlines = (UserSubscriptionInline, TransactionInline)
admin.site.register(Subscription, SubscriptionAdmin)


class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ( '__unicode__', _user, _subscription, 'active', 'expires')
    list_display_links = ( '__unicode__', )
    list_filter = ('active', 'subscription', 'expires')
    date_hierarchy = 'expires'
    ordering = ('-expires',)

admin.site.register(UserSubscription, UserSubscriptionAdmin)

class TransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('timestamp', 'id', 'event', _subscription, _user, _ipn, 'amount', 'comment')
    list_display_links = ('timestamp', 'id')
    list_filter = ('subscription', 'user')
admin.site.register(Transaction, TransactionAdmin)

class UserAdminSubscription(UserAdmin):
    inlines = (UserSubscriptionInline, TransactionInline)
 
admin.site.unregister(User)
admin.site.register(User, UserAdminSubscription)
