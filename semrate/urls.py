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

    #url(r'^accounts/register', 'registration.views.register', {'backend':'registration.backends.default.DefaultBackend', 'template_name':'registration_form.html'}),
    #url(r'^accounts/login', 'registration.views.register', {'backend':'registration.backends.default.DefaultBackend', 'template_name':'login.html'}),

    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^messages/', include('django_messages.urls')),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.PROJECT_PATH,'site_media') }),
    
    
    url(r'^advanced_search$','review.views.advanced_search'),
    url(r'^newproduct$', 'review.views.newproduct'),
	url(r'^newcategory$', 'review.views.newcategory'),
	url(r'^categories$', 'review.views.categories'),
	url(r'^category(?P<slug>.*)$', 'review.views.category'),
    url(r'^$', 'review.views.index'),
    
    #url(r'^ajax_createparameter$', 'review.views.ajax_createparameter'),
    url(r'^create_parameter$', 'review.views.create_parameter'),
    url(r'^ajax_createtag$', 'review.views.ajax_createtag'),
    url(r'^rate_parameter$', 'review.views.rate_parameter'),
    
    
	url(r'^products(?P<path>.*)$', 'review.views.viewproduct', {}),
    url(r'^search$', 'review.views.searchproduct', {}),
    
    url(r'^login', 'review.views.login'),
    url(r'^notable_for', 'review.views.notable_for'),
    url(r'^rdf(?P<slug>.*)$', 'review.views.rdf', {}),
    
    url(r'^add_product_fb','review.views.add_product_fb'),

	url(r'^edit_category(?P<slug>.*)$', 'review.views.edit_category'),

	url(r'^delete_category_parameter', 'review.views.delete_category_parameter'),

	url(r'^create_category_parameter', 'review.views.create_category_parameter'),
	url(r'^user/(?P<username>.*)$', 'review.views.user'),
	url(r'^follow/(?P<username>.*)$', 'review.views.follow'),
	url(r'^unfollow/(?P<username>.*)$', 'review.views.unfollow'),
	url(r'^fbtest$', 'review.views.fbtest'),

    
)
