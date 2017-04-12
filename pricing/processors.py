from pricing.models import *
from django.template import Context
from django.db.models import Count

# Custom Django context processor methods 
# Allow you to set up data for access on all templates
def settings(request):
	settings = {
		"COMPANY_NAME": 'HEALTHCARE PRICING',
		"COMPANY_EMAIL": 'email@pricing.com',
		"COMPANY_PHONE": '+1 999-999-9999',		
	}
	return {'SETTINGS': settings}

def data(request):
	all_procedures = Procedure.objects.all()
	common_procedures = all_procedures.annotate(num_services=Count('services')).order_by('-num_services')

	all_specialties = Specialty.objects.all().order_by('-name')

	data = {
		"ALL_PROCEDURES": all_procedures.order_by('name'),
		"COMMON_PROCEDURES": common_procedures,

		"ALL_SPECIALTIES": all_specialties,

	}
	return {'DATA': data}	