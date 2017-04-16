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
    url(r'^register-user/$', pricing_views.register_user, name='register_user'),
    url(r'^register-doctor/$', pricing_views.register_doctor, name='register_doctor'),
    url(r'^login/$', pricing_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),

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
    ###### USER PROFILE & SETTINGS ######
    url(r'^dashboard/user/$', pricing_views.user_dashboard, name='user_dashboard'),
    url(r'^dashboard/doctor/$', pricing_views.doctor_dashboard, name='doctor_dashboard'),    

	###### DOCTOR / CLINIC LISTS ######
	url(r'^doctors/procedure/(?P<procedure_name>[\w-]+)/(?P<procedure_id>[\d+]+)/$', pricing_views.view_doctors_by_procedure, name='view_doctors_by_procedure'),
    url(r'^doctors/specialty/(?P<specialty_slug>[\w-]+)/$', pricing_views.view_doctors_by_specialty, name='view_doctors_by_specialty'),
	url(r'^doctor/(?P<doctor_name>[\w-]+)/(?P<doctor_id>\d+)/$', pricing_views.view_doctor, name='view_doctor'),

    ###### DIRECTORIES ######
    url(r'^directory/$', pricing_views.directory, name='directory'),
	
    ##############################
    #     SUPPORTING URLS        #
    ##############################
    # DJANGO_AUTOCOMPLETE_LIGHT 
	 url(r'^procedure-autocomplete/$', pricing_views.ProcedureAutocomplete.as_view(), name='procedure-autocomplete',),
	 url(r'^zipcode-autocomplete/$', pricing_views.ZipcodeAutocomplete.as_view(), name='zipcode-autocomplete',),
     url(r'^city-autocomplete/$', pricing_views.CityAutocomplete.as_view(), name='city-autocomplete',),

     url(r'^search-form/(?P<request_url>[\w/-]+)/$', pricing_views.search_form, name='search_form',),

    ##############################
    #        WEBSITE URLS        #
    ##############################
    url(r'^$', pricing_views.home, name='home'),
    url(r'^about/$', pricing_views.about, name='about'),
    url(r'^contact-us/$', pricing_views.contact, name='contact'),
    url(r'^blog/$', pricing_views.blog, name='blog'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
