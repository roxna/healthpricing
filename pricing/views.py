# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from dal import autocomplete  #django_auto_complete
from pricing.forms import *
# from pricing.utils import *
import pdb

####################################
###       SET UP / GENERAL       ### 
####################################

def home(request):
	search_form = SearchServiceForm(request.POST or None)
	if request.method == 'POST':
		if search_form.is_valid():
			# Track the search request
			search = search_form.save(commit=False)
			search.source = 1
			search.save()

			procedure = get_object_or_404(Procedure, name=search_form.cleaned_data['procedure'])
			# zipcode = get_object_or_404(Zipcode, name=search_form.cleaned_data['zipcode'])
			city = get_object_or_404(City, name=search_form.cleaned_data['city'])
			
			# Redirect to doctors page
			# return redirect('view_doctors_by_procedure', slugify(city), slugify(procedure.name), procedure.id)

			# Redirect to view_doctors page with query parameters = city
	        redirect_url = reverse('view_doctors_by_procedure', kwargs={
	        	'procedure_name': slugify(procedure.name), 
	        	'procedure_id': procedure.id,
	        })
	        query_params = '?city=' + slugify(city.name)
	        return HttpResponseRedirect (redirect_url + query_params)
	data = {
		'search_form': search_form,
	}
	return render(request, "home.html", data)


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

def terms(request):
	data = {}	
	return render(request, "settings/terms.html", data)	


####################################
###         WEBSITE PAGES        ### 
####################################

def about(request):
	data = {}	
	return render(request, "website/about.html", data)	

def contact(request):
	data = {}	
	return render(request, "website/contact.html", data)	

def blog(request):
	data = {}	
	return render(request, "website/blog.html", data)		

####################################
###       DOCTORS / CLINICS      ### 
####################################

def view_doctors_by_procedure(request, procedure_name, procedure_id):
	procedure = get_object_or_404(Procedure, pk=procedure_id)	
	services = Service.objects.filter(procedure=procedure)
	doctors = DoctorProfile.objects.filter(services__in=services)

	if request.method == 'GET':
		# Get the query parameters from the url
		city_slug = request.GET.get('city')
		city = City.objects.filter(slug=city_slug)

		if city:
			doctors = doctors.filter(clinics__city__in=city)

		max_price = request.GET.get('max_price')
		if max_price and int(max_price) != -1:  #max_price = -1 --> no max_price defined
			doctors = doctors.filter(services__avg_price__lte=int(max_price))

		# zipcode = request.GET.get('zipcode')
		# zipcode = Zipcode.objects.filter(name=zipcode)
		# if zipcode:
		# 	doctors = doctors.filter(clinics__zipcode__in=zipcode)

		gender_int = request.GET.get('gender')
		if gender_int and int(gender_int) in [1, 2]:  #M(1) F(2)
			doctors.filter(user__gender=int(gender_int))

		review_score = request.GET.get('review_score')
		if review_score and int(review_score) in [3, 4, 5]:
			doctors.annotate(review_score=Avg('reviews__overall_score')).filter(review_score__gte=int(review_score))

	data = {
		'procedure': procedure,
		'doctors': doctors,
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
	
	doctor_review_form = ReviewForm(request.POST or None)
	doctor_review_form.fields['service'].queryset = Service.objects.filter(doctor=doctor)

	if request.method == 'POST' and request.user.is_authenticated():
		# Only save review if user logged in is a user (user_profile)
		# ...and review_form is_valid
		if request.user.user_profile and doctor_review_form.is_valid():
			review = doctor_review_form.save(commit=False)
			review.doctor = doctor
			review.author = request.user.user_profile
			review.overall_score = (doctor_review_form.cleaned_data['service_quality_score'] + doctor_review_form.cleaned_data['price_transparency_score'])/2			
			review.save()
			messages.success(request, 'Review added successfully')
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	# Show related doctors with the same specialties
	specialtys = Specialty.objects.filter(doctor=doctor)
	related_doctors = DoctorProfile.objects.filter(specialtys__in=specialtys).exclude(pk=doctor.id)
										 # .annotate(num_leads=Count('leads')).order_by('-num_leads')
	data = {
		'doctor': doctor,
		'doctor_review_form': doctor_review_form,
		'related_doctors': related_doctors,
	}	
	return render(request, "search/view_doctor.html", data)

# def view_doctor(request, doctor_name, doctor_id, procedure_name, procedure_id):
# 	doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
# 	procedure = get_object_or_404(Procedure, pk=procedure_id)
# 	service = Service.objects.filter(procedure=procedure, doctor=doctor)[0]
# 	doctor_review_form = ReviewForm(request.POST or None)
# 	if request.method == 'POST' and request.user.is_authenticated():
# 		# Only save review if user logged in is a user (user_profile)
# 		# ...and review_form is_valid
# 		if request.user.user_profile and doctor_review_form.is_valid():
# 			review = doctor_review_form.save(commit=False)
# 			review.doctor = doctor
# 			review.service = service
# 			review.author = request.user.user_profile
## 			review.overall_score = (doctor_review_form.cleaned_data['service_quality_score'] + doctor_review_form.cleaned_data['price_transparency_score'])/2
# 			review.save()
# 			messages.success(request, 'Review added successfully')
# 			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
# 	services = Service.objects.filter(procedure__pk=procedure_id)
# 	related_doctors = DoctorProfile.objects.filter(services__in=services).exclude(pk=doctor.id).annotate(num_leads=Count('leads')).order_by('-num_leads')

# 	data = {
# 		'doctor': doctor,
# 		'procedure': procedure,
# 		'service': service,
# 		'procedure_reviews': Review.objects.filter(doctor=doctor, service__procedure=procedure),
# 		'doctor_review_form': doctor_review_form,

# 		'related_doctors': related_doctors,
# 	}	
# 	return render(request, "search/view_doctor.html", data)

@login_required()
def request_appointment(request):
	# service = get_object_or_404(Service, pk=service_id)
	lead = Lead.objects.create(service=service, user=request.user.user_profile, doctor=service.doctor, lead_type=2)
	messages.success(request, 'Appointment requested - doctor will contact you shortly')
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required()
def request_more_info(request):
	# service = get_object_or_404(Service, pk=service_id)
	lead = Lead.objects.create(service=service, user=request.user.user_profile, doctor=service.doctor, lead_type=1)
	messages.success(request, 'More info requested - doctor will contact you shortly')
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))	
	
####################################
###      PROFILE / SETTINGS      ### 
####################################	

@login_required()
def dashboard(request):
	data = {}	
	return render(request, "portal/dashboard.html", data)	

@login_required()
# @user_passes_test(is_user)
def user_profile(request):
	data = {}	
	return render(request, "portal/user_profile.html", data)	

@login_required()
# @user_passes_test(is_user)
def user_appointments(request):
	data = {}	
	return render(request, "portal/user_appointments.html", data)	

@login_required()
# @user_passes_test(is_doctor)
def doctor_profile(request):
	data = {}	
	return render(request, "portal/doctor_profile.html", data)	

@login_required()
# @user_passes_test(is_doctor)
def doctor_appointments(request):
	data = {}	
	return render(request, "portal/doctor_appointments.html", data)				