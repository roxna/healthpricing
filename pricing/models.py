from __future__ import unicode_literals

from django.conf import settings as conf_settings
from django.contrib.auth.models import AbstractUser
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.utils import timezone
import numpy as np

###################################
###        USER DETAILS        ### 
################################### 

class User(AbstractUser):
	# Already has username, firstname, lastname, email, is_staff, is_active, date_joined
	pass

	def __unicode__(self):
		return self.username

	@property
	def is_user(self):
		return hasattr(self, 'user_profile')


class UserProfile(models.Model):	
	user = models.OneToOneField(User, related_name="user_profile")		

	def __unicode__(self):
		return self.user.username


###################################
###    PROVIDER  INFO          ### 
################################### 

class NameSlug(models.Model):
	name = models.CharField(max_length=50, default='')
	slug = models.CharField(max_length=50, default='')

	class Meta:
		abstract = True
	
	def __unicode__(self):
		return self.name

class State(NameSlug):
	pass
	# name = models.IntegerField(choices=conf_settings.STATES, null=True, blank=True)

class City(NameSlug):
	state = models.ForeignKey(State, related_name='cities')

class Zipcode(NameSlug):
	city = models.ForeignKey(City, related_name='zipcodes')

# File will be uploaded to MEDIA_ROOT/providers/<provider_name>/<filename>
def provider_img_directory_path(instance, filename):
	return 'providers/{0}/{1}'.format(instance.name, filename)

class Provider(models.Model):
	name = models.CharField(max_length=30, null=True, blank=True) #eg. Blue Dot Dental or Dr. Yung's Dental Clinic
	comments = models.CharField(max_length=500, null=True, blank=True)	
	is_verified = models.BooleanField(default=False)
	address1 = models.CharField(max_length=40, null=True, blank=True)
	address2 = models.CharField(max_length=40, null=True, blank=True)
	city = models.ForeignKey(City, related_name='clinics', null=True, blank=True)
	state = models.ForeignKey(State, related_name='clinics', null=True, blank=True)
	zipcode = models.ForeignKey(Zipcode, related_name='clinics', null=True, blank=True)
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.")
	phone = models.CharField(max_length=15, validators=[phone_regex], null=True, blank=True)
	email = models.EmailField(max_length=254, null=True, blank=True)
	image = models.ImageField(upload_to=provider_img_directory_path, blank=True, null=True)

	class Meta:
		get_latest_by = 'id'

	def __unicode__(self):
		return self.name

 	@property
	def image_url(self):
	    if self.image and hasattr(self.image, 'url'):
	        return self.image.url
	    else:
	    	return static('img/defaults/doctor.jpg')

	def get_average_stars(self):
		try:
			return int(UserPricePoint.objects.aggregate(Avg('stars'))['reviews__avg']) + 1
		except:
			return 0  

	def get_address_line1(self):
		return "{}, {}".format(self.address1, self.address2)

	def get_address_line2(self):
		return "{}, {} {}".format(self.city, self.state, self.zipcode)

###################################
###         PROCEDURES          ### 
################################### 

# Eg. Dental/Vision/Labs etc
class Category(NameSlug):
	pass

# Eg. Cavities/Orthodontics etc
class Subcategory(NameSlug):
	category = models.ForeignKey(Category, related_name='subcategories')

# File will be uploaded to MEDIA_ROOT/<procedure-name>/<filename>
def procedure_img_directory_path(instance, filename):
	return 'procedures/{0}/{1}'.format(instance.slug, filename)

class Procedure(models.Model):
	name = models.CharField(max_length=50)  #eg. Root Canal
	slug = models.CharField(max_length=50)  #eg. root-canal
	desc = models.CharField(max_length=500)
	image = models.ImageField(upload_to=procedure_img_directory_path, blank=True, null=True)	
	cpt_code = models.CharField(max_length=30, null=True, blank=True)
	category = models.ForeignKey(Category, related_name='procedures', null=True, blank=True)
	subcategory = models.ForeignKey(Subcategory, related_name='procedures', null=True, blank=True)
	# Acc to ACA, self-pay patients can't be charged more than Medicare patients.
	# Caveat - these prices will vary by user's Zip/location
	free_market_price = models.IntegerField(validators=[MinValueValidator(0)], default=0)
	insurer_price = models.IntegerField(validators=[MinValueValidator(0)], default=0)  
	billed_price = models.IntegerField(validators=[MinValueValidator(0)], default=0)  

	def __unicode__(self):
		return self.name

 	@property
	def image_url(self):
	    if self.image and hasattr(self.image, 'url'):
	        return self.image.url
	    else:
	    	return static('img/defaults/procedure.png')


###################################
###       PRICE POINTS          ### 
################################### 

# File will be uploaded to MEDIA_ROOT/user_prices/<user_email>/<filename>
def user_price_img_directory_path(instance, filename):
	return 'user_prices/{0}/{1}'.format(instance.user.email, filename)

class UserPricePoint(models.Model):
	price = models.IntegerField(validators=[MinValueValidator(0)])
	date = models.DateField(null=True, blank=True)
	comments = models.CharField(max_length=250, null=True, blank=True)	
	procedure = models.ForeignKey(Procedure, related_name="user_prices", null=True, blank=True)
	user = models.ForeignKey(UserProfile, related_name="user_prices")
	provider = models.ForeignKey(Provider, related_name='user_prices')
	stars = models.IntegerField(choices=conf_settings.SCORE_CHOICES, default=5)
	avg_wait_time = models.IntegerField(null=True, blank=True) #in num_days
	image = models.ImageField(upload_to=user_price_img_directory_path, blank=True, null=True)

	def __unicode__(self):
		return u"${}".format(self.price)

 	@property
	def image_url(self):
	    if self.image and hasattr(self.image, 'url'):
	        return self.image.url
	    else:
	    	return static('img/defaults/doctor.jpg')  #TODO: Update this

class MedicarePricePoint(models.Model):
	procedure = models.ForeignKey(Procedure, related_name="medicare_prices", null=True, blank=True)
	state = models.ForeignKey(State, related_name='medicare_prices', null=True, blank=True)


###################################
###            WEBSITE          ### 
###################################

class Search(models.Model):
	procedure = models.ForeignKey(Procedure, related_name='searches', null=True, blank=True)
	city = models.ForeignKey(City, related_name='searches', null=True, blank=True)
	zipcode = models.ForeignKey(Zipcode, related_name='searches', null=True, blank=True)
	source = models.CharField(max_length=50, default='/')


class Author(models.Model):
	name = models.CharField(max_length=40, null=True, blank=True)
	SOURCES = ((1, 'Blog'), (2, 'Testimonial'), (3, 'Contact Form'), (4, 'Newsletter'))
	source = models.IntegerField(choices=SOURCES, default=2)
	title = models.CharField(max_length=40, null=True, blank=True)
	company = models.CharField(max_length=50, null=True, blank=True)
	email = models.EmailField(max_length=254, null=True, blank=True)	

	def __unicode__(self):
		return "{}".format(self.name)

# File will be uploaded to MEDIA_ROOT/<blog_slug>/<filename>
def blog_img_directory_path(instance, filename):
	return 'blogs/{0}/{1}'.format(slugify(instance.title), filename)

class Blog(models.Model):
	title = models.CharField(max_length=100)
	summary = models.TextField()
	content1 = models.TextField()
	content2 = models.TextField(null=True, blank=True)
	quote1 = models.CharField(max_length=100, default='')
	quote2 = models.CharField(max_length=100, null=True, blank=True)
	date = models.DateField(default=timezone.now)
	image = models.ImageField(upload_to=blog_img_directory_path, blank=True, null=True)
	author = models.ForeignKey(Author, related_name="blogs")

	def __unicode__(self):
		return "{}".format(self.title)

 	@property
	def image_url(self):
	    if self.image and hasattr(self.image, 'url'):
	        return self.image.url
	    else:
	    	return static('img/defaults/blog.jpg')

class ContactRequest(models.Model):
	topic = models.IntegerField(choices=conf_settings.CONTACT_TOPICS, default=0)
	author = models.ForeignKey(Author, related_name="contact_requests")		
	date = models.DateTimeField(default=timezone.now)
	comments = models.TextField(null=True, blank=True)

	def __unicode__(self):
		return "{}({})".format(self.topic, self.author.name)

class Testimonial(models.Model):
	title = models.CharField(max_length=40, null=True, blank=True)
	comments = models.CharField(max_length=250)
	author = models.ForeignKey(Author, related_name="testimonials")
	date = models.DateTimeField(default=timezone.now)        

	def __unicode__(self):
		return "{}".format(self.title)