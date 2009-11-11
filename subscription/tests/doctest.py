### -*- coding: utf-8 -*- ####################################################
"""
>>> from subscription.models import Subscription, UserSubscription

Let's create couple of subscriptions
>>> silver = Subscription.objects.create(name='silver plan', price=17, recurrence_period=1, recurrence_unit='W')
>>> gold = Subscription.objects.create(name='gold plan', price=40, recurrence_period=5, recurrence_unit='D')

Create test user
>>> from django.contrib.auth.models import User
>>> test_user = User.objects.create_user('test_user', 'test@example.com', 'testpw')

User's subscription. By default every user has free subscription after adding
>>> test_user.subscription
<UserSubscription: test_user's Free Membership>

Subscribe our test user to silver plan
>>> us = UserSubscription.objects.create(user=test_user, subscription=silver)

By default, subscription expires in one week.
>>> from datetime import datetime, timedelta
>>> us.expires.date() == (datetime.now()+timedelta(7)).date()
True

User's subscription
>>> test_user.subscription
<UserSubscription: test_user's silver plan>

Let's get user's permissions

Firstly, check backend. We use special backend, he extend default ModelBackend by subscription's permissions 
>>> from django.conf import settings
>>> 'subscription.backends.UserSubscriptionBackend' in settings.AUTHENTICATION_BACKENDS
True
>>> test_user.get_all_permissions()
set([])

Add some permission
>>> from django.contrib.auth.models import Permission
>>> from django.contrib.contenttypes.models import ContentType
>>> perm = Permission.objects.create(name="test", 
...            content_type=ContentType.objects.get(name="subscription"), codename="test")
>>> perm
<Permission: subscription | subscription | test>
>>> silver.permissions.add(perm)
>>> silver.save()

Again, get user's permissions 
>>> test_user.get_all_permissions()
set([u'subscription.test'])

Unsubscribe
>>> us.active = False
>>> us.save()

Just to flush a cache
>>> test_user = User.objects.get(username='test_user')

>>> test_user.get_all_permissions()
set([])


"""
