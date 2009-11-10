### -*- coding: utf-8 -*- ####################################################
"""
>>> from subscription.models import Subscription, UserSubscription

Let's create couple of subscriptions
>>> silver = Subscription.objects.create(name='silver plan', price=17, recurrence_period=1, recurrence_unit='W')
>>> gold = Subscription.objects.create(name='gold plan', price=40, recurrence_period=5, recurrence_unit='D')

Create test user
>>> from django.contrib.auth.models import User
>>> test_user = User.objects.create_user('test_user', 'test@example.com', 'testpw')

Subscribe our test user to silver plan
>>> us = UserSubscription.objects.create(user=test_user, subscription=silver)

By default, subscription expires in one week.
>>> from datetime import datetime, timedelta
>>> us.exrires == datetime.now()+timedelta(7)
True


"""
