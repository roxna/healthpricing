from django import template
# from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter(name='currency') 
def currency(number, num_decimals=0):
	if num_decimals == 0:
		number = int(number)
	else:
		number = round(number, num_decimals)
	return "${}".format(number)

@register.filter(name='times') 
def times(number):
	try:
		return range(int(number))
    # No reviews yet - converting 'n/a' into int doesn't work
	except ValueError:
		return -1

@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg


# To add query parameters to URL 
# or replace it with new value if it's there
@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()

#####################
#   MODEL METHODS   #
#####################

@register.simple_tag
@register.filter(name='get_nth_percentile_price')
def get_nth_percentile_price(procedure, percentile):
    return procedure.get_nth_percentile_price(percentile)

@register.simple_tag
def get_avg_service_price(doctor, procedure):
    return doctor.services.filter(procedure=procedure)[0].avg_price

# @register.simple_tag
# def get_service_price_low(doctor, procedure):
#     return doctor.services.filter(procedure=procedure)[0].price_low

# @register.simple_tag
# def get_service_price_high(doctor, procedure):
#     return doctor.services.filter(procedure=procedure)[0].price_high
