from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from pricing.forms import *
from pricing.models import *

# Used for method decorator @user_passes_test
def is_user(user):
    return user.user_profile

def is_doctor(user):
    return user.doctor_profile


def redirect_per_search_query(procedure, city):
	# Redirect to 'view_doctors_by_procedure' page
	# with relevant query parameters = city_slug/no max_price, review_score, gender
    redirect_url = reverse('view_doctors_by_procedure', kwargs={
    	'procedure_name': procedure.slug, 
    	'procedure_id': procedure.id,
    })
    query_params = '?city=' + city.slug + '&max_price=-1&review_score=-1&gender=-1'
    redirect_to = '%s%s' % (redirect_url, query_params)
    return HttpResponseRedirect (redirect_to)
