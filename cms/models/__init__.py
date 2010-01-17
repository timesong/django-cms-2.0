from moderatormodels import *
from pagemodel import *
from permissionmodels import *
from pluginmodel import *
from titlemodels import *

from django.core.exceptions import ImproperlyConfigured
from cms import signals as s_import

from django.conf import settings as d_settings
from django.core.urlresolvers import get_resolver, get_script_prefix,\
    NoReverseMatch
import django.core.urlresolvers
from django.utils.encoding import iri_to_uri



def validate_settings():
    if not "django.core.context_processors.request" in d_settings.TEMPLATE_CONTEXT_PROCESSORS:
        raise ImproperlyConfigured('django-cms needs django.core.context_processors.request in settings.TEMPLATE_CONTEXT_PROCESSORS to work correctly.')
    if not 'mptt' in d_settings.INSTALLED_APPS:
        raise ImproperlyConfigured('django-cms needs django-mptt installed.')
    
def validate_dependencies():
    # check for right version of reversions
    if 'reversion' in d_settings.INSTALLED_APPS:
        from reversion.admin import VersionAdmin
        if not hasattr(VersionAdmin, 'get_urls'):
            raise ImproperlyConfigured('django-cms requires never version of reversion (VersionAdmin must contain get_urls method)')
        
def monkeypatch_reverse():
    django.core.urlresolvers.old_reverse = django.core.urlresolvers.reverse
    
    def new_reverse(viewname, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None):
        url = ''
        i18n = 'cms.middleware.multilingual.MultilingualURLMiddleware' in settings.MIDDLEWARE_CLASSES
        lang = None
        if viewname.split(":")[0] in dict(settings.LANGUAGES).keys():
            lang = viewname.split(":")[0]
        try:    
            url = django.core.urlresolvers.old_reverse(viewname, urlconf=urlconf, args=args, kwargs=kwargs, prefix=prefix, current_app=current_app)
            if lang:
                url = "/%s%s" % (lang, url)
        except NoReverseMatch, e:
            if i18n:            
                if not lang:
                    try:    
                        lang = get_language()
                        ml_viewname = "%s:%s" % ( lang, viewname)
                        url = django.core.urlresolvers.old_reverse(ml_viewname, urlconf=urlconf, args=args, kwargs=kwargs, prefix=prefix, current_app=current_app)
                        url = "/%s%s" % (lang, url)
                    except NoReverseMatch, e:
                        pass
        return url
    
    django.core.urlresolvers.reverse = new_reverse
        
validate_dependencies()
validate_settings()
monkeypatch_reverse()
