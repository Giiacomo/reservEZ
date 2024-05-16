# forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, Submit
from ..models import Restaurant, Address, MenuSection, Dish, OpeningHours
from ..utils.constants import WEEKDAYS

class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHours
        fields = ['weekday', 'opening_time', 'closing_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weekday'].widget = forms.Select(choices=WEEKDAYS)
        self.fields['opening_time'].widget = forms.TimeInput(format='%H:%M')
        self.fields['closing_time'].widget = forms.TimeInput(format='%H:%M')
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Add Opening Hours',
                Div(
                    Div('weekday', css_class='col-md-6'),
                    Div('opening_time', css_class='col-md-6'),
                    Div('closing_time', css_class='col-md-6'),
                    css_class='row'
                ),
            ),
            Submit('submit', 'Submit'),
        )

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'country', 'postal_code']

    def __init__(self, *args, **kwargs):
        existing_address = kwargs.pop('existing_address', None)
        super(AddressForm, self).__init__(*args, **kwargs)
        if existing_address:
            self.fields['street'].initial = existing_address.street
            self.fields['city'].initial = existing_address.city
            self.fields['state'].initial = existing_address.state
            self.fields['country'].initial = existing_address.country
            self.fields['postal_code'].initial = existing_address.postal_code

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'street',
            'city',
            'state',
            'country',
            'postal_code',
            Submit('submit', 'Submit', css_class='btn-success')
        )

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super(RestaurantForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            Submit('submit', 'Submit', css_class='btn-success')
        )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        # Check if a restaurant with the same name already exists
        if Restaurant.objects.filter(owner=self.user).exists():
            raise forms.ValidationError('A restaurant for this owner already exists .')
        return cleaned_data


class MenuSectionForm(forms.ModelForm):
    class Meta:
        model = MenuSection
        fields = ['sname']

    def __init__(self, *args, **kwargs):
        super(MenuSectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'sname',
            Submit('submit', 'Submit', css_class='btn-success')
        )
class DishForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super(DishForm, self).__init__(*args, **kwargs)
        if restaurant:
            self.fields['section'].queryset = MenuSection.objects.filter(menu__restaurant=restaurant)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'section',
            'dname',
            'description',
            'price',
            Submit('submit', 'Submit', css_class='btn-success')
        )

    section = forms.ModelChoiceField(queryset=MenuSection.objects.none())

    class Meta:
        model = Dish
        fields = ['dname', 'description', 'price', 'section']