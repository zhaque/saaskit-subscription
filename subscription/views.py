import urllib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template

_formclass = getattr(settings, 'SUBSCRIPTION_PAYPAL_FORM', 'paypal.standard.forms.PayPalPaymentsForm')
_formclass_dot = _formclass.rindex('.')
_formclass_module = __import__(_formclass[:_formclass_dot], {}, {}, [''])
PayPalForm = getattr(_formclass_module, _formclass[_formclass_dot+1:])

from subscription.models import Subscription, UserSubscription
from subscription.providers import PaymentMethodFactory
from subscription.forms import _paypal_form

# http://paypaldeveloper.com/pdn/board/message?board.id=basicpayments&message.id=621
if settings.PAYPAL_TEST:
    cancel_url = 'https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_subscr-find&alias=%s' \
                    % urllib.quote(settings.PAYPAL_RECEIVER_EMAIL)
else:
    cancel_url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_subscr-find&alias=%s' \
                    % urllib.quote(settings.PAYPAL_RECEIVER_EMAIL)

# https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_html_Appx_websitestandard_htmlvariables

@login_required
def subscription_standard_ipn(request, object_id, queryset=Subscription.objects.filter(price__gt=0), 
                        template_name='subscription/subscription_detail.html'):
    s = get_object_or_404(queryset, id=object_id)
    
    try:
        us = request.user.subscription
    except UserSubscription.DoesNotExist:
        change_denied_reasons = None
        us = None
    else:
        change_denied_reasons = us.try_change(s)

    if change_denied_reasons:
        form = None
    else:
        form = _paypal_form(s, request.user,
                            upgrade_subscription=(us is not None) and (us.subscription != s))
    
    return direct_to_template(request, template=template_name,
                  extra_context={'object': s, 'usersubscription': (us and us.subscription==s),
                                 'change_denied_reasons': change_denied_reasons,
                                 'form': form, 'cancel_url': cancel_url})

@login_required
def subscription_pro(request, object_id, queryset=Subscription.objects.filter(price__gt=0)):
    """Paypal Pro payment method """
    s = get_object_or_404(queryset, id=object_id)
    domain = Site.objects.get_current().domain
    item = {"amt": s.price,
            "inv": "inventory",         # unique tracking variable paypal
            "custom": "tracking",       # custom tracking variable for you
            "cancelurl": 'http://%s%s' % (domain, reverse('subscription_cancel')),  # Express checkout cancel url
            "returnurl": 'http://%s%s' % (domain, reverse('subscription_done'))}  # Express checkout return url
    
    data = {"item": item,
            "payment_template": "subscription/payment.html",      # template name for payment
            "confirm_template": "subscription/confirmation.html", # template name for confirmation
            "success_url": reverse('subscription_done')}              # redirect location after success
    
    o = PaymentMethodFactory.factory('WebsitePaymentsPro', data=data, request=request)
    # We return o.proceed() just because django-paypal's PayPalPro returns HttpResponse object
    return o.proceed()
