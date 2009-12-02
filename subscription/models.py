### -*- coding: utf-8 -*- ####################################################

import datetime

from django.conf import settings
from django.db import models
from django.contrib import auth
from django.utils.translation import ungettext, ugettext_lazy as _
from django.db.models.signals import post_init, post_save, pre_delete, pre_save

from paypal.standard.ipn.models import PayPalIPN 

from subscription import utils, signals

class Transaction(models.Model):
    
    EVENT_SUBSCRIBED = 1
    EVENT_PAYMENT = 2
    EVENT_PAYMENT_INCORRECT = 3
    EVENT_REMOVED = 4
    EVENT_ACTIVATED = 5
    EVENT_CANCELLED = 6
    EVENT_RECURED = 7
    
    EVENTS = (
        (EVENT_SUBSCRIBED, _('subscribed')),
        (EVENT_PAYMENT, _('payment')),
        (EVENT_PAYMENT_INCORRECT, _('payment incorrect')),
        (EVENT_REMOVED, _('removed')),
        (EVENT_ACTIVATED, _('activated')),
        (EVENT_CANCELLED, _('cancelled')),
        (EVENT_RECURED, _('recured')),
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    subscription = models.ForeignKey('subscription.Subscription', related_name='transactions',
                                     null=True, blank=True, )
    user = models.ForeignKey(auth.models.User, null=True, 
                             blank=True, 
                             related_name='subscription_transactions')
    ipn = models.ForeignKey(PayPalIPN, null=True, 
                            blank=True)
    event = models.PositiveSmallIntegerField(choices=EVENTS)
    amount = models.DecimalField(max_digits=64, decimal_places=2,
                                 null=True, blank=True)
    comment = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('-timestamp',)


_recurrence_unit_days = {
    'D' : 1.,
    'W' : 7.,
    'M' : 30.4368,                      # http://en.wikipedia.org/wiki/Month#Julian_and_Gregorian_calendars
    'Y' : 365.2425,                     # http://en.wikipedia.org/wiki/Year#Calendar_year
    }

class Subscription(models.Model):
    
    TIME_UNIT_CHOICES=(
        ('D', _('Day')),
        ('W', _('Week')),
        ('M', _('Month')),
        ('Y', _('Year')),
    )

    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(_('price'), max_digits=64, decimal_places=2, default=0)
    
    trial_unit = models.CharField(_("trial unit"), max_length=1, 
                                  choices=TIME_UNIT_CHOICES, default='W')
    trial_period = models.PositiveIntegerField(_("trial period"), default=0)
    
    recurrence_period = models.PositiveIntegerField(_("recurrence period"), default=1)
    recurrence_unit = models.CharField(_("recurrence unit"), max_length=1, 
                                       choices=TIME_UNIT_CHOICES, default='M')
    
    preparation_required = models.BooleanField(_("Admin should prepare environment"), default=False)
    
    permissions = models.ManyToManyField(auth.models.Permission)
     
    _PLURAL_UNITS = {
        'D': _('days'),
        'W': _('weeks'),
        'M': _('months'),
        'Y': _('years'),
        }

    class Meta:
        ordering = ('price','-recurrence_period')

    def __unicode__(self): return self.name

    def price_per_day(self):
        """Return estimate subscription price per day, as a float.

        This is used to charge difference when user changes
        subscription.  Price returned is an estimate; month length
        used is 30.4368 days, year length is 365.2425 days (averages
        including leap years).  One-time payments return 0.
        """
        if self.recurrence_unit is None:
            return 0
        return float(self.price) / self.recurrence_days()
    
    def recurrence_days(self):
        return self.recurrence_period*_recurrence_unit_days.get(self.recurrence_unit, 0)
    
    @models.permalink
    def get_absolute_url(self):
        return ( 'subscription_detail', (), dict(object_id=str(self.id)) )

    def get_pricing_display(self):
        if not self.price: return u'Free'
        elif self.recurrence_period:
            return ungettext('%(price).02f / %(unit)s',
                             '%(price).02f / %(period)d %(unit_plural)s',
                             self.recurrence_period) % {
                'price':self.price,
                'unit':self.get_recurrence_unit_display(),
                'unit_plural':_(self._PLURAL_UNITS[self.recurrence_unit],),
                'period':self.recurrence_period,
                }
        else: return _('%(price).02f one-time fee') % { 'price':self.price }

    def get_recurrence_display(self):
        if self.recurrence_period:
            return ungettext('One %(unit)s',
                             '%(period)d %(unit_plural)s',
                             self.recurrence_period) % {
                'unit':self.get_recurrence_unit_display().lower(),
                'unit_plural':_(self._PLURAL_UNITS[self.recurrence_unit],),
                'period':self.recurrence_period,
                }
        else:
            return _("No recurrence")
    
    def get_trial_display(self):
        if self.trial_period:
            return ungettext('One %(unit)s',
                             '%(period)d %(unit_plural)s',
                             self.trial_period) % {
                'unit':self.get_trial_unit_display().lower(),
                'unit_plural':_(self._PLURAL_UNITS[self.trial_unit],),
                'period':self.trial_period,
                }
        else:
            return _("No trial")
    
    def subscribe(self, user):
        try:
            existent = UserSubscription.objects.get(user=user)
        except UserSubscription.DoesNotExist:
            return self.user_subscriptions.create(user=user, subscription=self)
        else:
            if existent.subscription != self:
                existent.subscription = self
                existent.save()
                signals.subscribed.send(existent)
            
            existent.activate()
                
            return existent
    
SUBSCRIPTION_GRACE_PERIOD = getattr(settings, 'SUBSCRIPTION_GRACE_PERIOD', 2)

class UserSubscription(models.Model):
    user = models.OneToOneField(auth.models.User, related_name="subscription")
    subscription = models.ForeignKey(Subscription, related_name="user_subscriptions")
    expires = models.DateField(_('expires'))
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ( ('user','subscription'), )
        
    def __init__(self, *args, **kwargs):
        super(UserSubscription, self).__init__(*args, **kwargs)
        
        if self.expires is None: 
            period, unit = (self.subscription.trial_period, 
                            self.subscription.trial_unit) if self.subscription.trial_period \
                            else (self.subscription.recurrence_period,
                                self.subscription.recurrence_unit)
            
            self.expires = utils.extend_date_by(datetime.datetime.now(), period, unit)
    
    def expired(self):
        """Returns true if there is more than SUBSCRIPTION_GRACE_PERIOD
        days after expiration date."""
        grace_timedelta = datetime.timedelta(SUBSCRIPTION_GRACE_PERIOD)
        return self.expires is not None and (
            self.expires + grace_timedelta < datetime.date.today() )
    expired.boolean = True
    
    def extend(self, timedelta=None):
        """Extend subscription by `timedelta' or by subscription's
        recurrence period."""
        if timedelta is not None:
            self.expires += timedelta
        else:
            self.expires = utils.extend_date_by(
                            self.expires,
                            self.subscription.recurrence_period,
                            self.subscription.recurrence_unit)
        self.save()
        signals.recured.send(self)
        
    def activate(self):
        if not self.active:
            self.active = True
            self.save()
            signals.activated.send(self)
    
    def cancel(self):
        if self.active:
            self.active = False
            self.save()
            signals.cancelled.send(self)
    
    def try_change(self, subscription):
        """Check whether upgrading/downgrading to `subscription' is possible.

        If subscription change is possible, returns false value; if
        change is impossible, returns a list of reasons to display.

        Checks are performed by sending
        subscription.signals.change_check with sender being
        UserSubscription object, and additional parameter
        `subscription' being new Subscription instance.  Signal
        listeners should return None if change is possible, or a
        reason to display.
        """
        if self.subscription == subscription:
            if not self.active: return None # allow resubscribing
            return [ _(u'This is your current subscription.') ]
        return [
            res[1]
            for res in signals.change_check.send(
                self, subscription=subscription)
            if res[1] ]

    @models.permalink
    def get_absolute_url(self):
        return ( 'subscription_usersubscription_detail',
                 (), dict(object_id=str(self.id)) )

    def __unicode__(self):
        rv = u"%s's %s" % ( self.user, self.subscription )
        if self.expired():
            rv += u' (expired)'
        return rv
