from django import forms
from django.conf import settings as conf_settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, HTML
from dal import autocomplete
from pricing.models import *

####################################
###         REGISTRATION         ### 
####################################

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(required=True) 
    email = forms.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('firstname', css_class='col-md-6'),
                Div('lastname', css_class='col-md-6'),
                css_class='row',
            ), 
            Div(
                Div('username', css_class='col-md-6'),
                Div('email', css_class='col-md-6'),
                css_class='row',
            ), 
            Div(
                Div('password1', css_class='col-md-6'),
                Div('password2', css_class='col-md-6'),
                css_class='row',
            ),                     
        )
        self.helper.form_tag = False

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):        
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    def save(self, commit=True):
        user = super(RegisterUserForm, self).save(commit=False)
        # user.is_active = False  #User not active until activate account through email
        if commit:
            user.save()
        return user

class DoctorProfileForm(ModelForm):  
    username = forms.CharField(required=False, label='Personal Statement') 
    image = forms.ImageField(required=False, label='Photograph') 

    def __init__(self, *args, **kwargs):
        super(DoctorProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('title', css_class='col-md-8'),
                Div('years_experience', css_class='col-md-4'),
                css_class='row',
            ),
            Div(
                Div('comments', css_class='col-md-8'),
                Div('image', css_class='col-md-4'),
                css_class='row',
            ),            
        )

    class Meta:
        model = DoctorProfile
        fields = ("title", "comments", "image", "years_experience") 

class SearchServiceForm(ModelForm):
    procedure = forms.ModelChoiceField(
        required=True,
        queryset=Procedure.objects.all(),
        widget=autocomplete.ModelSelect2(url='procedure-autocomplete')) 
    # zipcode = forms.ModelChoiceField(
    #     required=True,
    #     queryset=Zipcode.objects.all(),
    #     widget=autocomplete.ModelSelect2(url='zipcode-autocomplete')) 
    city = forms.ModelChoiceField(
        required=True,
        queryset=City.objects.all(),
        widget=autocomplete.ModelSelect2(url='city-autocomplete')) 

    def __init__(self, *args, **kwargs):
        super(SearchServiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('procedure', css_class='col-md-7'),
                Div('city', css_class='col-md-3'),
                Submit('submit', 'Search', css_class='col-md-2 btn btn-primary btn-lg margin-top-25'),
                css_class='row',
            ),          
        )

    class Meta:
        model = Search
        fields = ("procedure", "city")

class ReviewForm(ModelForm):
    title = forms.CharField(required=True,)
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3, 'cols':60}))
    service_quality_score = forms.ChoiceField(choices=conf_settings.SCORE_CHOICES, required=True, label='Service Quality')
    price_transparency_score = forms.ChoiceField(choices=conf_settings.SCORE_CHOICES, required=True, label='Price Transparency')

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('title', css_class='col-md-6'),
                Div('service', css_class='col-md-6'),
                css_class='row',
            ),
            Div(
                Div('service_quality_score', css_class='col-md-6'),
                Div('price_transparency_score', css_class='col-md-6'),
                css_class='row',
            ),            
            Div(
                Div('comments', css_class='col-md-12'),           
                css_class='row',
            ),         
        )

    class Meta:
        model = Review
        fields = ("title", "service", "comments", "service_quality_score", "price_transparency_score")