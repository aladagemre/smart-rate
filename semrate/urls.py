from django.conf.urls.defaults import patterns, include, url
import os
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'semrate.views.home', name='home'),
    # url(r'^semrate/', include('semrate.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^facebook/', include('django_facebook.urls')),    
    url(r'^accounts/', include('registration.backends.default.urls')),
    
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.PROJECT_PATH,'site_media') }),
    
    url(r'^newproduct$', 'review.views.newproduct'),

    url(r'^$', 'review.views.index'),
    
    url(r'^ajax_createparameter$', 'review.views.ajax_createparameter'),
    url(r'^ajax_createtag$', 'review.views.ajax_createtag'),
    
    url(r'^products/(?P<path>.*)/$', 'review.views.viewproduct', {}),
    url(r'^search/$', 'review.views.searchproduct', {}),

)
