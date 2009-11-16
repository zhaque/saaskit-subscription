
from datetime import datetime

from django import forms
from django.contrib import admin
from django.utils.html import conditional_escape as esc

from subscription.models import Subscription, UserSubscription, Transaction
from subscription.utils import extend_date_by

def _pricing(sub): return sub.get_pricing_display()
def _trial(sub): return sub.get_trial_display()

#===============================================================================
# class SubscriptionAdminForm(forms.ModelForm):
#    class Meta:
#        model = Subscription
#===============================================================================
    
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', _pricing, _trial)
    filter_horizontal = ('permissions',)
admin.site.register(Subscription, SubscriptionAdmin)

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

class UserSubscriptionAdminForm(forms.ModelForm):
    class Meta:
        model = UserSubscription
    extend_subscription = forms.fields.BooleanField(required=False)

class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ( '__unicode__', _user, _subscription, 'active', 'expires')
    list_display_links = ( '__unicode__', )
    list_filter = ('active', 'subscription', )
    date_hierarchy = 'expires'
    form = UserSubscriptionAdminForm
#===============================================================================
#    
#    fieldsets = (
#        (None, {'fields' : ('user', 'subscription', 'expires', 'active')}),
#        ('Actions', {'fields' : ('extend_subscription',),
#                     'classes' : ('collapse',)}),
#        )
# 
#    def save_model(self, request, obj, form, change):
#        if form.cleaned_data['extend_subscription']:
#            obj.extend()
#        obj.save()
#===============================================================================

    # action for Django-SVN or django-batch-admin app
    actions = ( 'extend', )

    def extend(self, request, queryset):
        for us in queryset.all(): us.extend()
    extend.short_description = 'Extend subscription'

admin.site.register(UserSubscription, UserSubscriptionAdmin)

class TransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('timestamp', 'id', 'event', _subscription, _user, _ipn, 'amount', 'comment')
    list_display_links = ('timestamp', 'id')
    list_filter = ('subscription', 'user')
admin.site.register(Transaction, TransactionAdmin)
