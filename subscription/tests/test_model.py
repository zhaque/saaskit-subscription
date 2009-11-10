### -*- coding: utf-8 -*- ####################################################
#
# Copyright (c) 2009 Arvid Paeglit. All Rights Reserved.
#
##############################################################################
"""
$Id:interfaces.py 11316 2008-05-19 12:07:19Z arvid $
"""

from datetime import datetime, date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from bill import NotEnoughMoney

from trade.models import Product, PlumbLine, WorkFlow
from trade.engine import check_plumblines_status

class ModelTest(TransactionTestCase):
    fixtures = ['test_trade.json']
    
    def setUp(self):
        self.user = User.objects.get(username='testusername')
        
        self.product = Product.objects.get(slug='dazhe-ne-znayu-chto-eto')
        
        check_plumblines_status()
        
        self.active_pl = PlumbLine.objects.get(status='active')
        self.future_pl = PlumbLine.objects.get(status='future')
        self.finished_pl = PlumbLine.objects.get(status='finished')
        
    def tearDown(self):
        pass
    
    def test_activate(self):
        self.assertRaises(ValidationError, self.active_pl.activate)
        self.assertRaises(ValidationError, self.finished_pl.activate)
        
        self.future_pl.activate()
        self.assertEqual(self.future_pl.status, self.future_pl.STATUS_ACTIVE)
        
    def test_finish(self):
        self.assertRaises(ValidationError, self.future_pl.finish)
        self.assertRaises(ValidationError, self.finished_pl.finish)
        
        self.active_pl.finish()
        self.assertEqual(self.active_pl.status, self.active_pl.STATUS_FINISHED)
    
    def test_bidding_without_money(self):
        
        for i in range(16):
            self.active_pl.bid(self.user)
        
        latest_bid = WorkFlow.objects.filter(author=self.user, event='bid', 
                                             plumb_line=self.active_pl).latest('date')
        
        #user had 50.00 funds, and one bid costs 3.00, so 16*3 = 48 - successful bids, and 17s is not.
        self.assertRaises(NotEnoughMoney, lambda : self.active_pl.bid(self.user) )
        
        #We must check that new Workflow instance has not created
        self.assertEqual(latest_bid, WorkFlow.objects.filter(author=self.user, 
                                    event='bid', plumb_line=self.active_pl).latest('date'))
        