### -*- coding: utf-8 -*- ####################################################
#
# Copyright (c) 2009 Arvid Paeglit. All Rights Reserved.
#
##############################################################################
"""
$Id:interfaces.py 11316 2008-05-19 12:07:19Z arvid $
"""

from datetime import datetime, date, timedelta
import time

from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse

from workflow.models import Transition

from trade.models import Product, PlumbLine, WorkFlow, AuctionType
from trade.engine import check_plumblines_status, get_plumblines_of_user, \
reject_extended_purchases

class ClientTest(TransactionTestCase):
    fixtures = ['test_trade.json']
    
    def setUp(self):
        self.user = User.objects.get(username='testusername')
        self.client.login(username=self.user.username, password='test')
        
        self.user2 = User.objects.get(username='testusername2')
        
        self.product = Product.objects.get(slug='dazhe-ne-znayu-chto-eto')
        
        check_plumblines_status()
        
        self.active_pl = PlumbLine.objects.get(status='active')
        #self.future_pl = PlumbLine.objects.get(status='future')
        #self.finished_pl = PlumbLine.objects.get(status='finished')
        
    def tearDown(self):
        pass
    
    def test_plumbline_tab(self):
        search_url = reverse('plumb_line_list')
        response = self.client.get('/')
        
        #tab item
        self.assertContains(response, '<a href="%s">Plumb lines' % search_url)
        #all active items
        self.assertContains(response, '<a href="%s?status=active">Active auctions</a>' \
                                        % search_url )
        
        #check all active categories
        for cat_id, cat_name in ((2, 'Category1'), (4, 'Category11')):
            self.assertContains(response, '<a href="%s?status=active&category=%s">%s (1)</a>' \
                                            % (search_url, cat_id, cat_name) )
        
        #we must see no root category and not active category
        self.assertNotContains(response, 
                '<a href="%s?status=active&category=1">Root' % search_url )
        self.assertNotContains(response, 
                '<a href="%s?status=active&category=3">Category2' % search_url )
        
        #all future plumb lines
        self.assertContains(response, '<a href="%s?status=future">Future auctions</a>' \
                                        % search_url )
        #all finished auctions
        self.assertContains(response, '<a href="%s?status=finished">Finished auctions</a>' \
                                        % search_url )
    
    def test_product_tab(self):
        search_url = reverse('product_list')
        response = self.client.get('/')
        
        self.assertContains(response, '<a href="%s">Products' % search_url)
        
        #We should see all our categories without counts
        for cat_id, cat_name in ((2, 'Category1'), (4, 'Category11'), (3, 'Category2')):
            self.assertContains(response, '<a href="%s?category=%s">%s</a>' \
                                            % (search_url, cat_id, cat_name) )
        
        #But root category
        self.assertNotContains(response, '<a href="%s?category=1">Root' % search_url )
        
    def test_search_bar(self):
        search_url = reverse('plumb_line_list')
        response = self.client.get('/')
        
        self.assertContains(response, '<form method="get" class="search" action="%s">' % search_url)
        self.assertContains(response, 
            '<input type="text" title="Search active plumb lines" value="Search" size="25" id="search-text" name="q"')
        
        #Let's search with 'Test' query
        response = self.client.get(search_url, {'q': 'Test'})
        self.assertEqual(len(response.context['plumb_line_list']), 1)
        self.assertEqual(list(response.context['plumb_line_list'])[0], self.active_pl)
    
    def test_unauthorized(self):
        self.client.logout()
        
        response = self.client.get(reverse('plumb_line_detail', kwargs={'object_id': self.active_pl.id}))
        
        self.assertNotContains(response, "My bids")
        
        #Let's try to bid. I can not do it because of unauthorizing. 
        response = self.client.get(reverse('plumb_line_bid', kwargs={'plumb_line_id': self.active_pl.id}))
        self.assertRedirects(response, "/account/login?next=%s" \
                             % reverse('plumb_line_bid', kwargs={'plumb_line_id': self.active_pl.id}),
                             target_status_code=301)
        
    def test_bid(self):
        #We have no bids yet
        response = self.client.get(reverse('plumb_line_detail', kwargs={'object_id': self.active_pl.id}))
        #check title
        self.assertContains(response, '<h1><a href="%s">%s</a></h1>' \
                                        % (self.active_pl.product.get_absolute_url(),
                                           self.active_pl.product.title))
        
        #check bids 
        self.assertContains(response, '<p>Here are no bids.</p>')
        
        self.assertContains(response, '<tr><td>Current price:</td><td>0.00</td></tr>')
        self.assertContains(response, '<tr><td>Market price:</td><td>500.00</td></tr>')
        self.assertNotContains(response, '<tr><td>My bids (0):</td><td>0</td></tr>')
        self.assertContains(response, '<tr><td>Indemnification:</td><td>500.00</td></tr>')
        self.assertContains(response, '<tr><td>Economy:</td><td>0.00</td></tr>')
        
        #Let's bid
        self.assertContains(response, '<div class="plumb_line-bid"><a href="%s">Bid</a></div>' \
                                        % (reverse('plumb_line_bid', args=(self.active_pl.id,))))
        response = self.client.get(reverse('plumb_line_bid', kwargs={'plumb_line_id': self.active_pl.id}))
        self.assertRedirects(response, self.active_pl.get_absolute_url())
        
        response = self.client.get(reverse('plumb_line_detail', kwargs={'object_id': self.active_pl.id}))
        self.assertNotContains(response, '<p>Here are no bids.</p>')
        self.assertContains(response, '<td class="user"><a href="%s">%s</a></td>' \
                                        % (reverse('profile_detail', args=(self.user.username,)),
                                           self.user) )
        
        #Let's check the leader
        self.assertContains(response, '<span class="leader-member"><a href="%s">%s</a></span>' \
                                       % (reverse('profile_detail', args=(self.user.username,)),
                                           self.user) )
        
        self.assertContains(response, '<tr><td>Current price:</td><td>0.75</td></tr>')
        self.assertContains(response, '<tr><td>My bids (1):</td><td>3.00</td></tr>')
        self.assertContains(response, '<tr><td>Indemnification:</td><td>496.25</td></tr>')
        self.assertContains(response, '<tr><td>Economy:</td><td>0.00</td></tr>')
    
    def test_bid_expenses(self):
        #We have no expenses yet
        response = self.client.get(reverse('acct_bill'))
        self.assertContains(response, '<strong id="bill">50.00</strong>')
        
        self.assertEqual(len(response.context['expenses']), 0)
        
        #Let's bid
        response = self.client.get(reverse('plumb_line_bid', args=(self.active_pl.id,)))
        
        response = self.client.get(reverse('acct_bill'))
        self.assertContains(response, '<strong id="bill">47.00</strong>')
        
        
    def test_bidding_without_money(self):
        
        for i in range(17):
            response = self.client.get(reverse('plumb_line_bid', args=(self.active_pl.id,)))
        
        messages = self.user.get_and_delete_messages()
        #user had 50.00 funds, and one bid costs 3.00, so 16*3 = 48 - successful bids, and 17s is not.
        self.assertEqual(messages, [u'Your bid is accepted.']*16 + [u"You have not enough money"])
        
        #We must redirect user to bill page 
        self.assertRedirects(response, reverse('acct_bill'))
        
        #Check workflow history
        response = self.client.get(reverse('bid_history', args=(self.active_pl.id,) ))
        self.assertEqual(len(response.context['plumb_line'].get_bids()), 16)
    
    def _build_auction_cycle(self):
        auctionType = AuctionType.objects.get(id=5)
        auction = PlumbLine.objects.create(product=self.product, auction_type=auctionType, 
                            market_price=100)
        check_plumblines_status()
        auction = PlumbLine.objects.get(id=auction.id)
        
        auction.bid(self.user)
        auction.bid(self.user2)
        auction.bid(self.user)
        
        time.sleep(1)
        check_plumblines_status()
        auction = PlumbLine.objects.get(id=auction.id)
        
        self.assertEqual(auction.status, PlumbLine.STATUS_FINISHED)
        
        return auction
    
    def test_wins(self):
        auction = self._build_auction_cycle()
        
        response = self.client.get(reverse('plumb_line_detail', kwargs={'object_id': auction.id}))
        self.assertContains(response, 'Your state: Won just')
        self.assertContains(response, '<a href="purchase_right/">Details</a>')
        
        purchase_right_url = reverse('purchase_right_detail', kwargs={'object_id': auction.id})
        response = self.client.get(purchase_right_url)
        self.assertContains(response, '<p>Current state: Won just</p>')
        
        accept_url = reverse('progress_transition', 
                             kwargs={'object_id': 1, 
                                     'transition_id': Transition.objects.filter(name="Accept")[0].id})
        self.assertContains(response, 'href="%s">Accept</a>' % accept_url)
        response = self.client.get(accept_url)
        self.assertRedirects(response, purchase_right_url)
        
        response = self.client.get(purchase_right_url)
        self.assertContains(response, '<p>Current state: Accepted</p>')
        
        self.client.login(username='admin', password='vfhnsirf')
        admin_url = '/admin/trade/plumbline/%s/' % auction.id
        response = self.client.get(admin_url)
        
        deliver_url = reverse('progress_transition', 
                              kwargs={'object_id': auction.purchase_right.id, 
                                      'transition_id': Transition.objects.get(name="Start to deliver").id})
        self.assertContains(response, 'href="%s">Start to deliver</a>' % deliver_url)
        response = self.client.get(deliver_url)
        
        response = self.client.get(admin_url)
        given_url = reverse('progress_transition', 
                            kwargs={'object_id': auction.purchase_right.id, 
                                    'transition_id': Transition.objects.get(name="Give in").id})
        self.assertContains(response, 'href="%s">Give in</a>' % given_url)
        response = self.client.get(given_url)
        
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(purchase_right_url)
        self.assertContains(response, '<p>Current state: Bought</p>')
    
    def test_reject_wins(self):
        auction = self._build_auction_cycle()
        auction_url = reverse('plumb_line_detail', kwargs={'object_id': auction.id})
        response = self.client.get(auction_url)
        reject_url = reverse('progress_transition', 
                             kwargs={'object_id': 1, 
                                     'transition_id': Transition.objects.filter(name="Reject")[0].id})
        self.assertContains(response, 'href="%s">Reject</a>' % reject_url)
        
        response = self.client.get(reject_url)
        
        response = self.client.get(auction_url)
        self.assertContains(response, '<h3>Your state: Rejected</h3>')
        
        self.client.login(username=self.user2.username, password='test')
        response = self.client.get(auction_url)
        self.assertContains(response, 'Your state: A right passed to')
        
        accept_url = reverse('progress_transition', 
                             kwargs={'object_id': 1, 
                                     'transition_id': Transition.objects.filter(name="Accept")[1].id})
        self.assertContains(response, 'href="%s">Accept</a>' % accept_url)
        response = self.client.get(accept_url)
        
        response = self.client.get(auction_url)
        self.assertContains(response, '<h3>Your state: Accepted</h3>')
        
        #Let's relogin like first user
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(auction_url)
        self.assertContains(response, '<h3>Your state: Rejected</h3>')
    
    def test_not_accepts(self):
        auction = self._build_auction_cycle()
        
        #Set deadline equal to now
        current = auction.purchase_right.current_state()
        current.deadline = datetime.now()
        current.save()
        
        reject_extended_purchases()
        
        auction_url = reverse('plumb_line_detail', kwargs={'object_id': auction.id})
        response = self.client.get(auction_url)
        self.assertContains(response, 'Your state: Rejected')
        
        purchase_right_url = reverse('purchase_right_detail', kwargs={'object_id': auction.id})
        response = self.client.get(purchase_right_url)
        self.assertContains(response, "Did not accepted before deadline by %s" % self.user.username)
    
    def test_total_reject(self):
        """ all users reject a right on a purchase """
        auction = self._build_auction_cycle()
        
        reject_url = reverse('progress_transition', 
                             kwargs={'object_id': 1, 
                                     'transition_id': Transition.objects.filter(name="Reject")[0].id})
        response = self.client.get(reject_url)
        
        self.client.login(username=self.user2.username, password='test')
        
        reject_url = reverse('progress_transition', 
                             kwargs={'object_id': 1, 
                                     'transition_id': Transition.objects.filter(name="Reject")[1].id})
        response = self.client.get(reject_url)
        
        response = self.client.get(auction.get_absolute_url())
        self.assertContains(response, '<h3>Your state: Rejected</h3>')
        
        purchase_right_url = reverse('purchase_right_detail', kwargs={'object_id': auction.id})
        response = self.client.get(purchase_right_url)
        self.assertContains(response, "Cancel purchase workflow", count=1)
        self.assertContains(response, "Current state: Canceled")
        
        #After this, we give back all money
        response = self.client.get(reverse('acct_bill'))
        self.assertContains(response, '<strong id="bill">50.00</strong>')
        self.assertEqual(len(response.context['funds']), 2)
        self.assertEqual(float(response.context['funds'][0].cash), 1.00)
        
        #check first user's fund
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('acct_bill'))
        self.assertContains(response, '<strong id="bill">50.00</strong>')
        self.assertEqual(len(response.context['funds']), 2)
        self.assertEqual(float(response.context['funds'][0].cash), 2.00)
        
    def test_participation(self):
        profile_url = reverse('profile_detail', kwargs={'username': self.user.username})
        
        response = self.client.get(profile_url)
        self.assertNotContains(response, "Participated in auctions")
        
        self.active_pl.bid(self.user)
        
        response = self.client.get(profile_url)
        self.assertContains(response, "Participated in auctions")
        self.assertContains(response, '<a href="%s">%s</a>' \
                                % (self.active_pl.get_absolute_url(), self.active_pl) )
        
        auction = self._build_auction_cycle()
        response = self.client.get(profile_url)
        self.assertContains(response, '<a href="%s">%s</a>' \
                                % (auction.get_absolute_url(), auction) )
        self.assertContains(response, '<a href="%s">Won just</a>' \
                                % reverse('purchase_right_detail', args=(auction.id,) ) )
        
        response = self.client.get(reverse('profile_detail', kwargs={'username': self.user2.username}))
        self.assertContains(response, '<a href="%s">%s</a>' \
                                % (auction.get_absolute_url(), auction) )
        self.assertNotContains(response, '<a href="%s">' \
                                % reverse('purchase_right_detail', args=(auction.id,) ) )
    
    def test_won_notice(self):
        auction = self._build_auction_cycle()
        
        response = self.client.get(reverse('notification_notices'))
        self.assertContains(response, 'Won just <a href="%s">%s</a>' \
                                    % (auction.get_absolute_url(), auction) )
        