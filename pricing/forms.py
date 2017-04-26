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
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('first_name', css_class='col-md-6'),
                Div('last_name', css_class='col-md-6'),
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
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")

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

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
  
# Didn't use Django UserChangeForm because that requires PW
class ChangeUserForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ChangeUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields['username'].help_text = None
        self.helper.layout = Layout(
            # Field('username', css_class='form-control', readonly=True),
            # Field('email', css_class='form-control', readonly=True),
            Div(
                Div('first_name', css_class='col-md-6'),
                Div('last_name', css_class='col-md-6'),
                css_class='row',
            ),             
            Div(
                Div('username', css_class='col-md-6'),
                Div('email', css_class='col-md-6'),
                css_class='row',
            ), 
        )
        self.helper.form_tag = False

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

# class DoctorProfileForm(ModelForm):  
#     title = forms.CharField(required=False, label='Title (eg. MD)') 
#     image = forms.ImageField(required=False, label='Photograph') 
#     consultation_fee = forms.IntegerField(required=False, label='Initial Consultation Fee ($)', widget=forms.TextInput(attrs={
#         'placeholder': 'Tip: $0 sees the best results'
#     }))
#     comments = forms.CharField(required=False, widget=forms.Textarea(attrs={
#         'rows':3, 'cols':60, 
#         'placeholder': 'Please share a personal statement, experience, style of engagement etc'
#     }))

#     def __init__(self, *args, **kwargs):
#         super(DoctorProfileForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_tag = False
#         self.helper.layout = Layout(
#             Div(
#                 Div('title', css_class='col-md-6'),
#                 Div('gender', css_class='col-md-6'),
#                 css_class='row',
#             ),
#             Div(
#                 Div('years_experience', css_class='col-md-6'),
#                 Div('consultation_fee', css_class='col-md-6'),
#                 css_class='row',
#             ),
#             Div(
#                 Div('comments', css_class='col-md-12'),
#                 css_class='row',
#             ),      
#             Div(
#                 Div('image', css_class='col-md-6'),
#                 css_class='row',
#             ),                   
#         )

#     class Meta:
#         model = DoctorProfile
#         fields = ("title", "comments", "image", "years_experience", "gender", "consultation_fee") 


# class ClinicForm(ModelForm):
#     pass

#     def __init__(self, *args, **kwargs):
#         super(ClinicForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_tag = False
#         self.helper.layout = Layout(
#             Div(
#                 Div('name', css_class='col-md-12'),
#                 css_class='row',
#             ),
#             Div(
#                 Div('address1', css_class='col-md-6'),
#                 Div('address2', css_class='col-md-6'),
#                 css_class='row',
#             ),
#             Div(
#                 Div('city', css_class='col-md-6'),
#                 Div('zipcode', css_class='col-md-6'),
#                 css_class='row',
#             ),
#             Div(
#                 Div('phone', css_class='col-md-6'),
#                 Div('email', css_class='col-md-6'),
#                 css_class='row',
#             ),                        
#         )

#     class Meta:
#         model = Clinic
#         fields = ("name", "address1", "address2", "city", "zipcode", "phone", "email")     

class UserPricePointForm(ModelForm):
    procedure = forms.ModelChoiceField(
        required=True,
        queryset=Procedure.objects.all(),
        widget=autocomplete.ModelSelect2(url='procedure-autocomplete'))
    provider = forms.ModelChoiceField(
        required=True,
        queryset=Provider.objects.all(),
        widget=autocomplete.ModelSelect2(url='provider-autocomplete'))
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3, 'cols':60}))

    def __init__(self, *args, **kwargs):
        super(UserPricePointForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('procedure', css_class='col-md-6'),
                Div('provider', css_class='col-md-6'),
                css_class='row',
            ),   
            Div(
                Div('date', css_class='col-md-6'),
                Div('price', css_class='col-md-6'),
                css_class='row',
            ),  
            Div(
                Div('stars', css_class='col-md-6'),
                Div('avg_wait_time', css_class='col-md-6'),
                css_class='row',
            ),              
            Div(
                Div('comments', css_class='col-md-12'),
                css_class='row',
            ),                                               
        )

    class Meta:
        model = UserPricePoint
        fields = ("procedure", "provider", "date", "price", "stars", "avg_wait_time", "comments", "image")

class UserPricePointProcedureForm(ModelForm):
    provider = forms.ModelChoiceField(
        required=True,
        queryset=Provider.objects.all(),
        widget=autocomplete.ModelSelect2(url='provider-autocomplete'))
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3, 'cols':60}))

    def __init__(self, *args, **kwargs):
        super(UserPricePointProcedureForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('provider', css_class='col-md-12'),
                
                css_class='row',
            ),   
            Div(
                Div('price', css_class='col-md-6'),
                Div('date', css_class='col-md-6'),
                css_class='row',
            ),  
            Div(
                Div('comments', css_class='col-md-12'),
                css_class='row',
            ),
            Div(
                Div('stars', css_class='col-md-6'),
                Div('avg_wait_time', css_class='col-md-6'),
                css_class='row',
            ),                                                 
        )

    class Meta:
        model = UserPricePoint
        fields = ("provider", "date", "price", "stars", "avg_wait_time", "comments", "image")

class SearchServiceForm(ModelForm):
    procedure = forms.ModelChoiceField(
        required=True,
        queryset=Procedure.objects.all(),
        widget=autocomplete.ModelSelect2(url='procedure-autocomplete')) 
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
                Div('procedure', css_class='col-xs-12 col-sm-7 col-md-7 col-lg-7'),
                Div('city', css_class='col-xs-8 col-sm-4 col-md-4 col-lg-4'),
                Submit('search', '&#xf002;', css_class='col-xs-4 col-sm-1 col-md-1 col-lg-1 btn btn-primary btn-lg margin-top-20 btn-search-icon'),
            ),          
        )

    class Meta:
        model = Search
        fields = ("procedure", "city")



###################################
###            WEBSITE          ### 
###################################

class ContactRequestForm(ModelForm):
    topic = forms.ChoiceField(conf_settings.CONTACT_TOPICS, required=True)
    comments = forms.CharField(required=False, widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(ContactRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(                
                Div('topic', css_class='col-md-12'),
                Div('comments', css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        model = ContactRequest
        fields = ('topic', 'comments')   


class AuthorForm(ModelForm):
    name = forms.CharField(max_length=40, required=True)
    company = forms.CharField(required=False, max_length=50)
    email = forms.EmailField(max_length=254)

    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(                
                Div('name', css_class='col-md-12'),
                css_class='row',
            ),
            Div(                
                Div('company', css_class='col-md-6'),
                Div('email', css_class='col-md-6'),
                css_class='row',
            ),            
        )        

    class Meta:
        model = Author
        fields = ('name', 'company', 'email')

class NewsletterForm(ModelForm):
    email = forms.EmailField(max_length=254)

    def __init__(self, *args, **kwargs):
        super(NewsletterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(                
                Div('email', css_class='col-md-12'),
                css_class='row',
            ),
        )

    def save(self, commit=True):
        if self.clean():
            instance = super(NewsletterForm, self).save(commit=False)
            instance.source = 4
            if commit:
                instance.save()
            return instance

    class Meta:
        model = Author
        fields = ('email',)