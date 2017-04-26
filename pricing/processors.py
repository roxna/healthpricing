from pricing.models import *
from pricing.forms import SearchServiceForm
from django.template import Context
from django.db.models import Count

# Custom Django context processor methods 
# Allow you to set up data for access on all templates
def settings_processor(request):
	settings = {
		"COMPANY_NAME": 'HEALTHCARE PRICING',
		"COMPANY_EMAIL": 'email@pricing.com',
		"DOCTOR_SUPPORT_EMAIL": 'doctors@pricing.com',
		"COMPANY_PHONE": '+1 999-999-9999',
		"COMPANY_ADDRESS": '225 Richardson St, Australian',
	}
	return {'SETTINGS': settings}

def data_processor(request):
	data = {
		"ALL_PROCEDURES": Procedure.objects.order_by('name'),
		"ALL_PROVIDERS": Provider.objects.filter(is_verified=True).order_by('name'),
	}
	return {'DATA': data}

def forms_processor(request):
	search_form = SearchServiceForm()
	return {'search_form': search_form}
