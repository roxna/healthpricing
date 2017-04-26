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
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import is_safe_url
from django.utils.text import slugify
from django.utils import timezone
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
				messages.success(request, 'Awesome - stay tuned! In the meantime, check out our blogs for a healthier living!')
				return redirect('blogs')	
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

class ProviderAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Provider.objects.all()
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
###       DOCTORS / CLINICS      ### 
####################################

def provider_directory(request):
	return render(request, "providers/provider_directory.html")	

def view_doctors_by_procedure(request, procedure_slug):
	procedure = get_object_or_404(Procedure, slug=procedure_slug)	
	services = Service.objects.filter(procedure=procedure)
	doctors = DoctorProfile.objects.filter(is_verified=True, services__in=services).distinct('id')

	if request.method == 'GET':
		city, max_price, gender, review_score, zipcode = get_query_parameters(request)	
		doctors, zipcodes = filter_doctors_by_query_parameters(doctors, city, max_price, gender, review_score, zipcode)

	data = {
		'procedure': procedure,
		'doctors': doctors,

		'cities': City.objects.all(),
		'zipcodes': zipcodes,
		'percentile_list': [25, 50, 75],
	}	
	return render(request, "providers/view_doctors_by_procedure.html", data)

def view_doctors_by_specialty(request, specialty_slug):
	specialty = Specialty.objects.filter(slug=specialty_slug)	
	doctors = DoctorProfile.objects.filter(is_verified=True, specialtys__in=specialty).distinct('id')

	if request.method == 'GET':
		city, max_price, gender, review_score, zipcode = get_query_parameters(request)	
		doctors, zipcodes = filter_doctors_by_query_parameters(doctors, city, max_price, gender, review_score, zipcode)

	data = {
		'specialty': specialty[0],
		'doctors': doctors,

		'cities': City.objects.all(),
		'zipcodes': zipcodes,
		'percentile_list': [25, 50, 75],
	}	
	return render(request, "providers/view_doctors_by_specialty.html", data)

def view_doctor(request, doctor_name, doctor_id):
	doctor = get_object_or_404(Provider, pk=doctor_id)
	doctor_services = Service.objects.filter(doctor=doctor)
	
	# Show related doctors with the same specialties
	specialtys = Specialty.objects.filter(doctor=doctor)
	related_doctors = Provider.objects.filter(is_verified=True, specialtys__in=specialtys).exclude(pk=doctor.id)
										 # .annotate(num_leads=Count('leads')).order_by('-num_leads')
	data = {
		'doctor': doctor,
		'related_doctors': related_doctors,
	}	
	return render(request, "providers/view_doctor.html", data)
	

def share_price(request):
	price_point_form = UserPricePointForm(request.POST or None, request.FILES or None, prefix="price_point")
	price_point_form.fields['procedure'].queryset = Procedure.objects.all()
	price_point_form.fields['provider'].queryset = Provider.objects.all()

	if request.method == 'POST':
		if price_point_form.is_valid():
			# user_profile = User.objects.get_or_create(username=)
			price_point = price_point_form.save(commit=False)
			# price_point.procedure = procedure
			# price_point.user = user_profile
			price_point.save()
			messages.success(request, 'Thanks! This will help us improve the service')
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	data = {
		'price_point_form': price_point_form,
	}
	return render(request, "website/share_price.html", data)

####################################
###          PROCEDURES          ### 
####################################

def view_procedure(request, procedure_slug):
	procedure = get_object_or_404(Procedure, slug=procedure_slug)
	price_point_form = UserPricePointProcedureForm(request.POST or None, request.FILES or None, prefix="price_point")
	price_point_form.fields['provider'].queryset = Provider.objects.all()
	# related_doctors = Provider.objects.filter(is_verified=True, services__in=procedure.services.all())

	data = {
		'procedure': procedure,
		'price_point_form': price_point_form,
		# 'related_doctors': related_doctors,
	}
	return render(request, "procedures/view_procedure.html", data)

def procedure_directory(request):
	return render(request, "procedures/procedure_directory.html")


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
	return render(request, "website/about.html")

def how_works(request):
	return render(request, "website/how_works.html")

# def about_for_physicians(request):
# 	return render(request, "website/about_for_physicians.html")

def blogs(request):
	blogs = Blog.objects.all()
	data = {
		'blogs': blogs,
	}	
	return render(request, "website/blogs.html", data)	

def view_blog(request, blog_slug, blog_id):
	blog = get_object_or_404(Blog, pk=blog_id)
	try:
		prev_blog = get_object_or_404(Blog, pk=int(blog_id)-1)
	except:
		prev_blog = blog
	try:
		next_blog = get_object_or_404(Blog, pk=int(blog_id)+1)
	except:
		next_blog = blog
	data = {
		'blog': blog,
		'prev_blog': prev_blog,
		'next_blog': next_blog,
	}	
	return render(request, "website/view_blog.html", data)

def terms(request):
	data = {}	
	return render(request, "website/terms.html", data)			