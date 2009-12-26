from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.list_detail import object_list, object_detail
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from subscription.models import Subscription, Transaction
from subscription.decorators import pdf_response

details_view = 'subscription.views.subscription_pro' if settings.PAYPAL_PRO \
                else 'subscription.views.subscription_standard_ipn'

invoice_info = {
    'template_object_name': 'transaction', 
    'queryset': Transaction.objects.filter(event__exact=Transaction.EVENT_PAYMENT).select_related()
}

invoice_listing_info = {'template_name': 'invoice/invoice_history.html'}
invoice_listing_info.update(invoice_info)

invoice_detail_info = {'template_name': 'invoice/invoice.html'}
invoice_detail_info.update(invoice_info)

invoice_queryset_wrapper = lambda request, queryset: queryset.filter(user=request.user)


def wrapped_queryset(func, queryset_edit=lambda request, queryset: queryset):
    def wrapped(request, queryset, *args, **kwargs):
        return func(request, queryset_edit(request, queryset), *args, **kwargs)
    wrapped.__name__ = func.__name__
    return wrapped


urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.list_detail.object_list', 
        {'template_name': 'subscription/subscription_list.html',
         'queryset': Subscription.objects.all()}, name='subscription_list'),

    url(r'^(?P<object_id>\d+)/$', details_view, name='subscription_detail'),
    
    (r'^paypal/', include('paypal.standard.ipn.urls')),
    
    (r'^done/', login_required(direct_to_template), 
     {'template': 'subscription/subscription_done.html'}, 
     'subscription_done'),
    
    (r'^change-done/', login_required(direct_to_template), 
     {'template': 'subscription/subscription_change_done.html'}, 
     'subscription_change_done'),
    
    (r'^cancel/', login_required(direct_to_template), 
     {'template': 'subscription/subscription_cancel.html'}, 
     'subscription_cancel'),
     
    url(r'^invoice/$', 
        login_required(wrapped_queryset(object_list, invoice_queryset_wrapper)),
        invoice_listing_info, name='invoice_listing'),
    
    url(r'^invoice/(?P<object_id>[\d]+)/$', 
        pdf_response(login_required(wrapped_queryset(object_detail, invoice_queryset_wrapper))),
        invoice_detail_info, name='invoice_detail'), 
    
)
