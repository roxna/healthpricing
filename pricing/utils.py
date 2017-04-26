from django.conf import settings
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from pricing.forms import *
from pricing.models import *

# Used for method decorator @user_passes_test
def is_user(user):
    return hasattr(user, 'user_profile')

def is_doctor(user):
    return hasattr(user, 'doctor_profile')

def log_user_in(request, user, error_msg):
	if user is not None:
		login(request, user)				
	else:
		messages.info(request, 'Invalid credentials')

def get_query_parameters(request):
	'''
	Get the query parameters from the request url
	'''
	city = request.GET.get('city')  				# city_slug
	max_price = request.GET.get('max_price')		# -1=Undef
	gender = request.GET.get('gender')  			# gender_int (1=M, 2=F, -1=Undef)
	review_score = request.GET.get('review_score')	# min_num_stars
	zipcode = request.GET.get('zipcode')

	return city, max_price, gender, review_score, zipcode


def filter_doctors_by_query_parameters(doctors, city, max_price, gender, review_score, zipcode):
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

	if gender and int(gender) in (1, 2):  #M(1) F(2)
		doctors = doctors.filter(gender=int(gender))				
	
	if review_score and int(review_score) in (3, 4, 5):
		# Get all doctors whose average review_scores are greater than requested
		# TODO: REFINE / Not scaleable (doctors.annotate(review_score=Avg('reviews__overall_score')).filter(review_score__gte=int(review_score))?)
		doctors_with_review_score = [doctor.id for doctor in DoctorProfile.objects.all() if doctor.get_review_score() >= int(review_score)]
		doctors = doctors.filter(pk__in=doctors_with_review_score)

	return doctors, zipcodes

def redirect_per_search_query(procedure, city):
	# Redirect to 'view_doctors_by_procedure' page
	# with relevant query parameters = city_slug/no max_price, review_score, gender
    redirect_url = reverse('view_doctors_by_procedure', kwargs={
    	'procedure_slug': procedure.slug,
    })
    query_params = '?city=' + city.slug + '&max_price=-1&review_score=-1&gender=-1'
    redirect_to = '%s%s' % (redirect_url, query_params)
    return HttpResponseRedirect (redirect_to)


