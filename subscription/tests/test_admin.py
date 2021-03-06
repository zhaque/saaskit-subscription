### -*- coding: utf-8 -*- ####################################################

from datetime import datetime, date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse

class AdminTest(TransactionTestCase):
    fixtures = ['test_subscription.json']
    
    def setUp(self):
        self.user = User.objects.get(username='admin')
        self.client.login(username=self.user.username, password='admin')
        
    def tearDown(self):
        pass
    
#===============================================================================
#    def test_login(self):
#        self.client.login(username='testusername', password='test')
#        response = self.client.get('/admin/')
#        self.assertContains(response, '<title>Log in | Django site admin</title>')
#        
#        
#        response = self.client.post('/admin/', {'username': self.user.username, 
#                                               'password': 'vfhnsirf',
#                                               'this_is_the_login_form': 1})
#        self.assertRedirects(response, '/admin/')
#    
#    def test_change_form_intermit(self):
#        response = self.client.get('/admin/trade/plumbline/%i/' % self.active_pl.id)
#        self.assertContains(response, '<a href="intermit/">Intermit</a>')
#        self.assertNotContains(response, '<a href="intermit/">Continue</a>')
#        
#        #Let's intermit this auction
#        response = self.client.get('/admin/trade/plumbline/%i/intermit/' % self.active_pl.id)
#        
#        self.assertEqual(self.user.get_and_delete_messages(), 
#                         [u'Successfully intermited or unintermited.'])
# 
#        self.assertRedirects(response, '/admin/trade/plumbline/%i/' % self.active_pl.id)
#        
#        response = self.client.get('/admin/trade/plumbline/%i/' % self.active_pl.id)
#        self.assertNotContains(response, '<a>Intermit</a>')
#        self.assertContains(response, '<a href="intermit/">Continue</a>')
#        
#        response = self.client.get('/admin/trade/plumbline/%i/intermit/' % self.active_pl.id)
#        self.assertRedirects(response, '/admin/trade/plumbline/%i/' % self.active_pl.id)
#    
#    def test_change_list_intermit(self):
#        change_list_url = '/admin/trade/plumbline/'
#        response = self.client.get(change_list_url)
#        self.assertEqual(list(response.context[-1]['cl'].result_list), 
#                         [self.future_pl, self.active_pl, self.finished_pl])
#        
#        response = self.client.post(change_list_url, 
#                                    {'_selected_action': [1,2,3], 
#                                     'index': 0, 
#                                     'action': 'do_intermit'})
#        
#        self.assertEqual(self.user.get_and_delete_messages(), 
#                         [u'1 plumb line was successfully intermited or unintermited.', 
#                          u'#3. Test title. Inactive auction can not act', 
#                          u'#1. Test title. Inactive auction can not act'])
#        
#        self.assertRedirects(response, change_list_url)
#        
#        #Let's continue intermited auction
#        response = self.client.post(change_list_url, 
#                                    {'_selected_action': [2], 
#                                     'index': 0, 
#                                     'action': 'do_intermit'})
#        self.assertEqual(self.user.get_and_delete_messages(), 
#                [u'1 plumb line was successfully intermited or unintermited.'])
#        self.assertRedirects(response, change_list_url)
#===============================================================================