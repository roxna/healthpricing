from __future__ import unicode_literals

from django.conf import settings as conf_settings
from django.contrib.auth.models import AbstractUser
from django.contrib.staticfiles.templatetags.staticfiles import static
# from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
# from django.db.models import Avg
# from django.template.defaultfilters import slugify
from django.utils import timezone
# import os
import numpy as np

###################################
###        USER DETAILS        ### 
################################### 

# File will be uploaded to MEDIA_ROOT/<buyer_co_name>/<filename>
def doctor_img_directory_path(instance, filename):
	return 'doctor_profiles/{0}/{1}'.format(instance.user.username, filename)

class User(AbstractUser):
    # Already has username, firstname, lastname, email, is_staff, is_active, date_joined
	GENDER_CHOICES = (
		# (-1, 'Unknown'),
		# (0, 'Any'),
		(1, 'Male'),
		(2, 'Female'),
	)
	gender = models.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)

	def __unicode__(self):
		return self.username	

class UserProfile(models.Model):	
	user = models.OneToOneField(User, related_name="user_profile")		

	def __unicode__(self):
		return self.user.username

class DoctorProfile(models.Model):	
	user = models.OneToOneField(User, related_name="doctor_profile")
	title = models.CharField(max_length=30) #eg. MD (Dr. John Doe, MD)
	consultation_fee = models.IntegerField(validators=[MinValueValidator(0)])
	comments = models.CharField(max_length=500, null=True, blank=True)
	image = models.ImageField(upload_to=doctor_img_directory_path, default='defaults/profile_pic.jpg', blank=True, null=True)
	years_experience = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
	# Have the Doc's qualifications been verified by us...
	# ...with state medical boards, are they board certified in their specialty etc
	is_verified = models.BooleanField(default=False) 

	def __unicode__(self):
		return self.user.username

 	@property
	def image_url(self):
	    if self.image and hasattr(self.image, 'url'):
	        return self.image.url
	    else:
	    	return 'defaults/grid.jpg'

	def get_full_name(self):
		return u"Dr {} {} {}".format(self.user.first_name, self.user.last_name, self.title)

	def get_review_score(self):
		total_score = 0
		num_reviews = self.reviews.count()
		if num_reviews == 0:
			return 'n/a'
		else:
			for review in self.reviews.all():
				total_score += review.overall_score
			return total_score/num_reviews

# Parent model for Specialties, Education, Hospital Affiliations, Languages, Board Certifications, Awards
class Qualification(models.Model):
	name =	models.CharField(max_length=50)
	slug = models.CharField(max_length=50, default='')
	doctor = models.ForeignKey(DoctorProfile, related_name='%(class)ss')
	
	def __unicode__(self):
		return self.name

	class Meta:
		abstract = True

# Doctor can multiple Specialities (eg. Internal Medicine, Cardiology) with a primary one
class Specialty(Qualification): 
	is_primary = models.BooleanField(default=False)	

class Education(Qualification):
	pass

class Affiliation(Qualification):
	pass

class Language(Qualification):
	pass

class Certification(Qualification):
	pass

class Award(Qualification):
	pass


###################################
###      CLINIC / SERVICES      ### 
################################### 

class Procedure(models.Model):
	name = models.CharField(max_length=30)  #eg. Root Canal
	slug = models.CharField(max_length=30, default='')  #eg. root-canal
	category = models.CharField(max_length=30)  #eg. Dental/Vision/Labs etc
	subcategory = models.CharField(max_length=30)  #eg. Cavities/Orthodontics etc
	cpt_code = models.CharField(max_length=30, null=True, blank=True)
	# Acc to ACA, self-pay patients can't be charged more than Medicare patients.
	# However, this price will vary by user's Zip/location
	fair_price = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)  

	def __unicode__(self):
		return self.name

	def get_nth_percentile_price(self, n):
		prices = []
		for service in self.services.all():
			prices.append(service.avg_price) 
		return int(np.percentile(prices, n))


class CityStateZipCountry(models.Model):
	name = models.CharField(max_length=20, default='')
	slug = models.CharField(max_length=20, default='')

	class Meta:
		abstract = True
	
	def __unicode__(self):
		return self.name	

class Neighborhood(CityStateZipCountry):
	pass

class City(CityStateZipCountry):
	pass

class State(CityStateZipCountry):
	pass

class Zipcode(CityStateZipCountry):
	pass

class Country(CityStateZipCountry):
	pass
	# name = models.IntegerField(choices=conf_settings.COUNTRIES, null=True, blank=True)		

class Clinic(models.Model):	
	name = models.CharField(max_length=30)
	address1 = models.CharField(max_length=40, null=True, blank=True)
	address2 = models.CharField(max_length=40, null=True, blank=True)
	neighborhood = models.ForeignKey(Neighborhood, related_name='clinics', null=True, blank=True)
	city = models.ForeignKey(City, related_name='clinics', null=True, blank=True)
	state = models.ForeignKey(State, related_name='clinics', null=True, blank=True)
	zipcode = models.ForeignKey(Zipcode, related_name='clinics', null=True, blank=True)
	country = models.ForeignKey(Country, related_name='clinics', null=True, blank=True)
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.")
	phone = models.CharField(max_length=15, validators=[phone_regex], null=True, blank=True)
	email = models.EmailField(max_length=254, null=True, blank=True)
	doctor = models.ForeignKey(DoctorProfile, related_name="clinics")
	
	def __unicode__(self):
		return self.name

	class Meta:
		get_latest_by = 'id'

	def get_average_review_score(self):
		try:
			return int(Clinic.objects.aggregate(Avg('reviews'))['reviews__avg']) + 1
		except:
			return 0   


# Specific Service Offering from a Specific Clinic/Doctor for a selected Procedure
class Service(models.Model):
	procedure = models.ForeignKey(Procedure, related_name='services')
	clinic = models.ForeignKey(Clinic, related_name='services')
	doctor = models.ForeignKey(DoctorProfile, related_name='services')
	# Price for self_pay on same day as service
	avg_price = models.IntegerField(validators=[MinValueValidator(0)])
	comments = models.CharField(max_length=500, null=True, blank=True)
	telemedicine_offered = models.BooleanField(default=False)
	avg_wait_time = models.IntegerField(null=True, blank=True) #in num_days

	def __unicode__(self):
		return u"{}".format(self.procedure.name)

	def get_average_review_score(self):
		try:
			return int(Service.objects.aggregate(Avg('reviews'))['reviews__avg']) + 1
		except:
			return 0


###################################
###           REVIEWS           ### 
################################### 

class Review(models.Model):
	title = models.CharField(max_length=30, null=True, blank=True)
	comments = models.CharField(max_length=250, null=True, blank=True)	
	date = models.DateField(default=timezone.now)
	doctor = models.ForeignKey(DoctorProfile, related_name="reviews")
	service = models.ForeignKey(Service, related_name="reviews")
	# Add a field for Clinic being reviewed?
	author = models.ForeignKey(UserProfile, related_name="reviews", null=True, blank=True)	
	service_quality_score = models.IntegerField(choices=conf_settings.SCORE_CHOICES)
	price_transparency_score = models.IntegerField(choices=conf_settings.SCORE_CHOICES)
	overall_score = models.IntegerField(choices=conf_settings.SCORE_CHOICES, default=5)
	# quality, safety, patient experience, price_transparency

	class Meta:
		get_latest_by = 'id'

	def __unicode__(self):
		return u"{}".format(self.title)


###################################
###       TRACK INTEREST        ### 
###################################

class Lead(models.Model):
	date_requested = models.DateTimeField(default=timezone.now)
	service = models.ForeignKey(Service, related_name='leads', null=True, blank=True)
	user = models.ForeignKey(UserProfile, related_name='leads')
	doctor = models.ForeignKey(DoctorProfile, related_name='leads')
	LEAD_TYPES = (
		(1, 'More Info'),
		(2, 'Appt Info'),
	)
	lead_type = models.IntegerField(choices=LEAD_TYPES)

	def __unicode__(self):
		return u"{} [{}]".format(self.service.procedure.name, self.doctor.get_full_name())


class Search(models.Model):
	procedure = models.ForeignKey(Procedure, related_name='searches', null=True, blank=True)
	city = models.ForeignKey(City, related_name='searches', null=True, blank=True)
	zipcode = models.ForeignKey(Zipcode, related_name='searches', null=True, blank=True)
	SOURCE_CHOICES = (
		(1, 'Home Page'),
		(2, 'xx'),
	)
	source = models.IntegerField(choices=SOURCE_CHOICES)


