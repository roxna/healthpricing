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
		"COMPANY_PHONE": '+1 999-999-9999',
		"COMPANY_ADDRESS": '225 Richardson St, Australian',
	}
	return {'SETTINGS': settings}

def data_processor(request):
	all_procedures = Procedure.objects.all()
	common_procedures = all_procedures.annotate(num_services=Count('services')).order_by('-num_services')

	all_specialties = Specialty.objects.all().order_by('name')

	data = {
		"ALL_PROCEDURES": all_procedures.order_by('name'),
		"COMMON_PROCEDURES": common_procedures,

		"ALL_SPECIALTIES": all_specialties,
		"ALL_DOCTORS": DoctorProfile.objects.all().order_by('user__first_name'),

	}
	return {'DATA': data}

def forms_processor(request):
	search_form = SearchServiceForm()
	# forms = {
	# 	'search_form': SearchServiceForm(request.POST or None),
	# }
	# return {'FORMS': forms}
	return {'search_form': search_form}
