# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from pricing.models import *

class UserAdmin(admin.ModelAdmin):
   list_display = ['id', 'username', 'email']

class UserProfileAdmin(admin.ModelAdmin):
   list_display = ['id', 'user']

class ProviderAdmin(admin.ModelAdmin):
   list_display = ['id', 'name', ]   


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Provider, ProviderAdmin)

class ProcedureAdmin(admin.ModelAdmin):
   list_display = ['id', 'name', 'category', 'subcategory']  

class NameSlugAdmin(admin.ModelAdmin):
   list_display = ['id', 'name',]


admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(Category, NameSlugAdmin)
admin.site.register(Subcategory, NameSlugAdmin)
admin.site.register(Zipcode, NameSlugAdmin)
admin.site.register(City, NameSlugAdmin)
admin.site.register(State, NameSlugAdmin)


class AuthorAdmin(admin.ModelAdmin):
   list_display = ['id', 'name'] 

class BlogAdmin(admin.ModelAdmin):
   list_display = ['id', 'title', 'author'] 

class ContactRequestAdmin(admin.ModelAdmin):
   list_display = ['id', 'topic', 'author'] 

class TestimonialAdmin(admin.ModelAdmin):
   list_display = ['id', 'title', 'author'] 

admin.site.register(Author, AuthorAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(ContactRequest, ContactRequestAdmin)
admin.site.register(Testimonial, TestimonialAdmin)

