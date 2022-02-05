from django.http import  HttpResponseRedirect
from django.urls import reverse
import urllib.parse 


def is_number(s):
    try:
        float(s)
        return True
    except:
        return False

# USE:  redirect_with_params('main-domain:index', param1='value1', param2='value2')
def redirect_with_params(viewname, **kwargs):
    """
    Redirect a view with params
    """
    rev = reverse(viewname)

    params = urllib.parse.urlencode(kwargs)
    if params:
        rev = '{}?{}'.format(rev, params)

    return rev