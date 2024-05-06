from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password', 'cell_number', 'name']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'user-registration-form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'email',
            'password',
            'cell_number',
            'name',
            Submit('submit', u'Submit', css_class='btn btn-success'), 
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_cell_number(self):
        cell_number = self.cleaned_data.get('cell_number')
        if User.objects.filter(cell_number=cell_number).exists():
            raise forms.ValidationError("This cell number is already in use.")
        return cell_number
