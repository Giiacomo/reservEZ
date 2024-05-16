from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.contrib.auth.models import User
from .models import Address
from django.contrib.auth.forms import UserCreationForm

    
class UserRegistrationForm (UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'user-registration-form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'email',
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',
            Submit('submit', u'Submit', css_class='btn btn-success'), 
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
        }

    def __init__(self, *args, **kwargs):
        existing_user = kwargs.pop('existing_user', None)
        super(UserInfoForm, self).__init__(*args, **kwargs)
        if existing_user:
            self.fields['username'].initial = existing_user.username
            self.fields['first_name'].initial = existing_user.first_name
            self.fields['last_name'].initial = existing_user.last_name
            self.fields['email'].initial = existing_user.email

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'country', 'postal_code']

    def __init__(self, *args, **kwargs):
        existing_address = kwargs.pop('existing_address', None)
        super(AddressForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'street',
            'city',
            'state',
            'country',
            'postal_code',
            Submit('submit', 'Update')
        )
        if existing_address:
            self.fields['street'].initial = existing_address.street
            self.fields['city'].initial = existing_address.city
            self.fields['state'].initial = existing_address.state
            self.fields['country'].initial = existing_address.country
            self.fields['postal_code'].initial = existing_address.postal_code