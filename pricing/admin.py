# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from pricing.models import *

class UserAdmin(admin.ModelAdmin):
   list_display = ['id', 'username', 'email']

class UserProfileAdmin(admin.ModelAdmin):
   list_display = ['id', 'user']

class DoctorProfileAdmin(admin.ModelAdmin):
   list_display = ['id', 'user', 'title', ]   

class QualificationAdmin(admin.ModelAdmin):
   list_display = ['id', 'name', 'doctor']


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(DoctorProfile, DoctorProfileAdmin)

admin.site.register(Specialty, QualificationAdmin)
admin.site.register(Education, QualificationAdmin)
admin.site.register(Affiliation, QualificationAdmin)

class ProcedureAdmin(admin.ModelAdmin):
   list_display = ['id', 'name', 'category', 'subcategory']  

class ClinicAdmin(admin.ModelAdmin):
   list_display = ['id', 'name', 'doctor'] 

class CityStateZipCountryAdmin(admin.ModelAdmin):
   list_display = ['id', 'name',]

class ServiceAdmin(admin.ModelAdmin):
   list_display = ['id', 'procedure', 'doctor', 'clinic', 'avg_price']         


admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(Clinic, ClinicAdmin)
admin.site.register(Zipcode, CityStateZipCountryAdmin)
admin.site.register(City, CityStateZipCountryAdmin)
admin.site.register(State, CityStateZipCountryAdmin)
admin.site.register(Country, CityStateZipCountryAdmin)
admin.site.register(Service, ServiceAdmin)

class LeadAdmin(admin.ModelAdmin):
   list_display = ['id', 'service', 'user', 'doctor'] 

class ReviewAdmin(admin.ModelAdmin):
   list_display = ['id', 'title', 'comments'] 

admin.site.register(Lead, LeadAdmin)
admin.site.register(Review, ReviewAdmin)


class AuthorAdmin(admin.ModelAdmin):
   list_display = ['id', 'name'] 

class BlogAdmin(admin.ModelAdmin):
   list_display = ['id', 'title', 'author'] 

class ContactRequestAdmin(admin.ModelAdmin):
   list_display = ['id', 'topic', 'author'] 

class TestimonialAdmin(admin.ModelAdmin):
   list_display = ['id', 'title', 'author'] 

admin.site.register(Author, AuthorAdmin)
# admin.site.register(Blog, BlogAdmin)
admin.site.register(ContactRequest, ContactRequestAdmin)
admin.site.register(Testimonial, TestimonialAdmin)

