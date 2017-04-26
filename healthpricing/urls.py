from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from pricing import views as pricing_views
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^terms/$', pricing_views.terms, name='terms'),

    ##############################
    #   AUTHENTICATION URLS      #
    ##############################
    # Registration & Log In
    # url(r'^register/user/$', pricing_views.register_user, name='register_user'),
    # url(r'^register/doctor/$', pricing_views.register_doctor, name='register_doctor'),
    # url(r'^login/$', pricing_views.login, name='login'),
    # url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),

    # Reset Password
    # https://docs.djangoproject.com/en/1.10/_modules/django/contrib/auth/views/
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^password_change/$', auth_views.password_change, {'post_change_redirect': 'home'}, name='password_change'),

    ##############################
    #      APPLICATION URLS      #
    ##############################

	###### DOCTORS ######
	url(r'^providers/directory/$', pricing_views.provider_directory, name='provider_directory'),
    url(r'^doctors/procedure/(?P<procedure_slug>[\w-]+)/$', pricing_views.view_doctors_by_procedure, name='view_doctors_by_procedure'),
    url(r'^doctors/specialty/(?P<specialty_slug>[\w-]+)/$', pricing_views.view_doctors_by_specialty, name='view_doctors_by_specialty'),
	url(r'^doctor/(?P<doctor_name>[\w-]+)/(?P<doctor_id>\d+)/$', pricing_views.view_doctor, name='view_doctor'),       

    
    ###### OTHER ########
    url(r'^share_price/$', pricing_views.share_price, name='share_price'),
	
    ###### DIRECTORIES ######    
    url(r'^procedures/directory/$', pricing_views.procedure_directory, name='procedure_directory'),
    url(r'^procedures/(?P<procedure_slug>[\w-]+)/$', pricing_views.view_procedure, name='view_procedure'), 

    ##############################
    #     SUPPORTING URLS        #
    ##############################
    ###### DJANGO_AUTOCOMPLETE_LIGHT ######
	 url(r'^procedure-autocomplete/$', pricing_views.ProcedureAutocomplete.as_view(), name='procedure-autocomplete',),
     url(r'^provider-autocomplete/$', pricing_views.ProviderAutocomplete.as_view(), name='provider-autocomplete',),
	 url(r'^zipcode-autocomplete/$', pricing_views.ZipcodeAutocomplete.as_view(), name='zipcode-autocomplete',),
     url(r'^city-autocomplete/$', pricing_views.CityAutocomplete.as_view(), name='city-autocomplete',),

     url(r'^search-form/(?P<request_url>[\w/-]+)/$', pricing_views.search_form, name='search_form',),

    ##############################
    #        WEBSITE URLS        #
    ##############################
    url(r'^$', pricing_views.home, name='home'),
    url(r'^about/$', pricing_views.about, name='about'),
    # url(r'^about/physicians/$', pricing_views.about_for_physicians, name='about_for_physicians'),
    url(r'^how-it-works/$', pricing_views.how_works, name='how_works'),
    url(r'^contact-us/$', pricing_views.contact, name='contact'),
    url(r'^blogs/$', pricing_views.blogs, name='blogs'),
    url(r'^blog/(?P<blog_slug>[\w-]+)/(?P<blog_id>[\w/-]+)/$', pricing_views.view_blog, name='view_blog'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
