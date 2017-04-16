# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
)
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Avg, Count
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
# from django.template import RequestContext
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import is_safe_url
from django.utils.text import slugify
from dal import autocomplete  #django_auto_complete
from pricing.forms import *
from pricing.utils import *
from pricing.processors import forms_processor
import pdb

####################################
###       SET UP / GENERAL       ### 
####################################

def home(request):
	search_form = SearchServiceForm(request.POST or None, prefix='search')
	newsletter_form = NewsletterForm(request.POST or None, prefix='newsletter')
	
	testimonials = Testimonial.objects.all().order_by('?')[:3]
	# rv = RequestContext(request, processors=['forms_processor'])
	# x = rv.get('FORMS')
	# print x
	if request.method == 'POST':
		if 'search' in request.POST:
			if search_form.is_valid():
				# Track the search request, search.source default is home page ('/')
				search = search_form.save()
				procedure = get_object_or_404(Procedure, name=search_form.cleaned_data['procedure'])
				city = get_object_or_404(City, name=search_form.cleaned_data['city'])
				return redirect_per_search_query(procedure, city)
		elif 'newsletter' in request.POST:
			if newsletter_form.is_valid():
				author = newsletter_form.save()
				return redirect('home')	
	data = {
		'search_form': search_form,
		'newsletter_form': newsletter_form,
		'testimonials': testimonials, 
	}
	return render(request, "home.html", data)

# Called in header of all pages (ref base_portal.html)
def search_form(request, request_url):
	procedure_id = int(request.POST['procedure'])
	city_id = int(request.POST['city'])
	procedure = get_object_or_404(Procedure, pk=procedure_id)
	city = get_object_or_404(City, pk=city_id)
	
	Search.objects.create(procedure=procedure, city=city, source=request_url)
	return redirect_per_search_query(procedure, city)

# DJANGO_AUTOCOMPLETE_LIGHT views
# Used in forms with autocomplete
class ProcedureAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Procedure.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

class ZipcodeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Zipcode.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = City.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs                

####################################
###         REGISTRATION         ### 
####################################

def register_user(request):
	user_form = RegisterUserForm(request.POST or None)  

	if request.method == "POST":
		if user_form.is_valid():
			user = user_form.save()
			user_profile = UserProfile.objects.create(user=user)

			authenticate(username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password1'])
			if user.is_authenticated():
				login(request, user)
			messages.success(request, 'Success. Registration successful')
			return redirect('login')
		else:
			messages.info(request, 'Error. Registration unsuccessful')
	data = {
		'user_form': user_form,
	}
	return render(request, "registration/register.html", data)

def register_doctor(request):
	user_form = RegisterUserForm(request.POST or None)  
	doctor_form = DoctorProfileForm(request.POST or None)
	
	if request.method == "POST":
		if  user_form.is_valid() and doctor_form.is_valid():
			user = user_form.save()
			doctor = doctor_form.save(commit=False)
			doctor.user = user
			doctor.save()
			
			authenticate(username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password1'])
			if user.is_authenticated():
				login(request, user)
			messages.success(request, 'Success. Registration successful')
			return redirect('login')
		else:
			messages.info(request, 'Error. Registration unsuccessful')
	data = {
		'user_form': user_form,
		'doctor_form': doctor_form
	}
	return render(request, "registration/register.html", data)

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
            	# OVERRIDDEN vs. django.contrib.auth.views.login function
            	# Redirects to user or doctor dashboard based on user's profile
            	if hasattr(request.user, 'user_profile'):
                	redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)		   # dashboard/user/
                elif hasattr(request.user, 'doctor_profile'):
                	redirect_to = resolve_url(settings.DOCTOR_LOGIN_REDIRECT_URL)  # dashboard/doctor/
            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)

def terms(request):
	data = {}	
	return render(request, "settings/terms.html", data)	
		

####################################
###       DOCTORS / CLINICS      ### 
####################################

def view_doctors_by_procedure(request, procedure_name, procedure_id):
	procedure = get_object_or_404(Procedure, pk=procedure_id)	
	services = Service.objects.filter(procedure=procedure)
	doctors = DoctorProfile.objects.filter(services__in=services)

	if request.method == 'GET':
		'''
		Get the query parameters from the url
		'''
		city = request.GET.get('city')  				# city_slug
		max_price = request.GET.get('max_price')		# -1=Undef
		gender = request.GET.get('gender')  			# gender_int (1=M, 2=F, -1=Undef)
		review_score = request.GET.get('review_score')	# min_num_stars
		zipcode = request.GET.get('zipcode')

		'''
		Filter the doctor list based on the query parameters
		'''
		if city and city != '-1':   					# city = -1 --> all cities
			city_obj = City.objects.filter(slug=city)
			doctors = doctors.filter(clinics__city__in=city_obj)
			zipcodes = Zipcode.objects.filter(city=city_obj)
		else:
			# If no city is selected in the filter, don't show the zipcode filter
			zipcodes = None

		if max_price and int(max_price) != -1:  		# max_price = -1 --> no max_price defined
			doctors = doctors.filter(services__avg_price__lte=int(max_price))
			
		if zipcode and int(zipcode) != -1:
			zipcode_obj = Zipcode.objects.filter(name=zipcode)
			doctors = doctors.filter(clinics__zipcode__in=zipcode_obj)

		if gender and int(gender) in [1, 2]:  #M(1) F(2)
			doctors.filter(gender=int(gender))
		
		if review_score and int(review_score) in [3, 4, 5]:
			# Get all doctors whose average review_scores are greater than requested
			# TODO: REFINE / Not scaleable (doctors.annotate(review_score=Avg('reviews__overall_score')).filter(review_score__gte=int(review_score))?)
			doctor_ids_with_review_score = [doctor.id for doctor in DoctorProfile.objects.all() if doctor.get_review_score() >= int(review_score)]
			doctors.filter(id__in=doctor_ids_with_review_score)			

	data = {
		'procedure': procedure,
		'doctors': doctors,

		'cities': City.objects.all(),
		'zipcodes': zipcodes,
		'percentile_list': [25, 50, 75],
	}	
	return render(request, "search/view_doctors_by_procedure.html", data)

def view_doctors_by_specialty(request, specialty_slug):
	specialty = Specialty.objects.filter(slug=specialty_slug)	
	doctors = DoctorProfile.objects.filter(specialtys__in=specialty)
	data = {
		'specialty': specialty[0],
		'doctors': doctors,
		'percentile_list': [25, 50, 75],
	}	
	return render(request, "search/view_doctors_by_specialty.html", data)

def view_doctor(request, doctor_name, doctor_id):
	doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
	
	login_form_appt = LoginForm(data=request.POST or None, prefix="login_appt")
	login_form_review = LoginForm(data=request.POST or None, prefix="login_review")

	doctor_review_form = ReviewForm(request.POST or None, prefix="review")
	doctor_review_form.fields['service'].queryset = Service.objects.filter(doctor=doctor)

	lead_form = LeadForm(request.POST or None, prefix="lead")
	lead_form.fields['service'].queryset = Service.objects.filter(doctor=doctor)

	if request.method == 'POST':
		if 'login_form_appt' in request.POST:
			# Authenticate and log in user
			# Then redirect them to the same page
			if login_form_appt.is_valid():
				user = authenticate(username=login_form_appt.cleaned_data['username'], password=login_form_appt.cleaned_data['password'])
				if user is not None:
					login(request, user)
					return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
				else:
					messages.info(request, 'Invalid credentials')
		elif 'login_form_review' in request.POST:
			if login_form_review.is_valid():
				user = authenticate(username=login_form_review.cleaned_data['username'], password=login_form_review.cleaned_data['password'])
				if user is not None:
					login(request, user)
					return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
				else:
					messages.info(request, 'Invalid credentials')
		elif 'doctor_review_form' in request.POST:
			# Only save review if user logged in, as a user (user_profile)
			# ...and review_form is_valid
			if request.user.is_authenticated() and request.user.user_profile and doctor_review_form.is_valid():
				review = doctor_review_form.save(commit=False)
				review.doctor = doctor
				review.user = request.user.user_profile
				review.overall_score = (int(doctor_review_form.cleaned_data['service_quality_score']) + int(doctor_review_form.cleaned_data['price_transparency_score']))/2
				review.save()
				messages.success(request, 'Review added successfully')
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		elif 'lead_form' in request.POST:
			if lead_form.is_valid():
				lead = lead_form.save(commit=False)
				lead.user = request.user.user_profile
				lead.doctor = doctor
				lead.lead_type = 2
				lead.save()
				messages.success(request, 'Request submitted successfully')
				return redirect('dashboard')
	
	# Show related doctors with the same specialties
	specialtys = Specialty.objects.filter(doctor=doctor)
	related_doctors = DoctorProfile.objects.filter(specialtys__in=specialtys).exclude(pk=doctor.id)
										 # .annotate(num_leads=Count('leads')).order_by('-num_leads')
	data = {
		'doctor': doctor,
		'login_form_appt': login_form_appt,
		'login_form_review': login_form_review,
		'doctor_review_form': doctor_review_form,
		'lead_form': lead_form,
		'related_doctors': related_doctors,
	}	
	return render(request, "search/view_doctor.html", data)
	

def directory(request):
	return render(request, "search/directory.html")

####################################
###      PROFILE / SETTINGS      ### 
####################################	

@login_required()
def user_dashboard(request):
	user_form = ChangeUserForm(request.POST or None, instance=request.user)
	user_profile = request.user.user_profile
	appt_requests = Lead.objects.filter(user=user_profile)
	reviews = Review.objects.filter(user=user_profile)
	if request.method == "POST":
		if user_form.is_valid():
			user_form.save()
			messages.success(request, "Profile updated successfully")
			return redirect('dashboard')
		else:
			messages.info(request, 'Error. Profile not updated')
	data = {
		'appt_requests': appt_requests,
		'reviews': reviews,
		'user_form': user_form,
	}		
	return render(request, "portal/user_dashboard.html", data)	

@login_required()
def doctor_dashboard(request):
	user_form = ChangeUserForm(request.POST or None, instance=request.user)
	doctor_profile = request.user.doctor_profile
	appt_requests = Lead.objects.filter(doctor=doctor_profile)
	doctor_profile_form = DoctorProfileForm(request.POST or None, instance=doctor_profile)
	if request.method == "POST":
		if user_form.is_valid() and doctor_profile_form.is_valid():
			user_form.save()
			doctor_profile_form.save()
			messages.success(request, "Profile updated successfully")
			return redirect('dashboard')
		else:
			messages.info(request, 'Error. Profile not updated')	
	data = {
		'doctor': doctor_profile,
		'appt_requests': appt_requests,
		'reviews': None,
		'user_form': user_form,
		'doctor_profile_form': doctor_profile_form,
	}	
	return render(request, "portal/doctor_dashboard.html", data)	

####################################
###          WEBSITE             ### 
####################################

def contact(request):
	author_form = AuthorForm(request.POST or None)
	contact_form = ContactRequestForm(request.POST or None)	
	if request.method == "POST":
		if contact_form.is_valid() and author_form.is_valid():
			author, created = Author.objects.get_or_create(**author_form.cleaned_data)
			if created:
				author.source = 1
				author.save()
			contact_request = contact_form.save(commit=False)
			contact_request.author=author
			contact_request.save()
			messages.success(request, 'Got your message - we will reach back out soon')
			return redirect('contact')
		else:
			messages.error(request, 'Error. Request not sent.')
	data = {
		'contact_form': contact_form,
		'author_form': author_form
	}
	return render(request, "website/contact.html", data)

def about(request):
	data = {}	
	return render(request, "website/about.html", data)	


def blog(request):
	data = {}	
	return render(request, "website/blog.html", data)	