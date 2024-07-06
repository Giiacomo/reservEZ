
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, Submit
from ..models import Restaurant, Address, Tag, MenuSection, Dish, OpeningHours
from ..utils.constants import WEEKDAYS, TAG_CHOICES
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime

class LogoUploadForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['logo']

class BannerUploadForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['banner']

class RestaurantTagForm(forms.ModelForm):
    tags = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Restaurant
        fields = ['tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].choices = TAG_CHOICES  

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', [])
        if len(tags) > 3:
            raise forms.ValidationError('You can select a maximum of 3 tags.')
        return tags

    def save(self, commit=True):
        instance = super().save(commit=False)
        tags_data = self.cleaned_data['tags']
        tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tags_data]  
        instance.tags.set(tags, clear=True)  
        if commit:
            instance.save()
        return instance


class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHours
        fields = ['weekday', 'opening_time', 'closing_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weekday'].widget = forms.Select(choices=WEEKDAYS)
        self.fields['opening_time']
        self.fields['closing_time']
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

    def clean(self):
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')

        if opening_time and closing_time:
            if not self.is_valid_time_format(opening_time):
                raise ValidationError("Invalid date format for opening time, use HH:MM.", code='invalid_opening_time')
            if not self.is_valid_time_format(closing_time):
                raise ValidationError("Invalid date format for closing time, use HH:MM.", code='invalid_closing_time')
            if opening_time >= closing_time:
                raise ValidationError("Closing time must be after opening time.", code='invalid_time_range')

        
        if opening_time is None and closing_time is not None:
            raise ValidationError("Opening time is required.", code='missing_opening_time')
        elif opening_time is not None and closing_time is None:
            raise ValidationError("Closing time is required.", code='missing_closing_time')

        return cleaned_data

    def is_valid_time_format(self, time_str):
        try:
            time_str = time_str.strftime('%H:%M') if isinstance(time_str, datetime.time) else time_str
            timezone.datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

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
        
        if Restaurant.objects.filter(owner=self.user, name=name).exists():
            raise forms.ValidationError('A restaurant with this name already exists for this owner.')
        return cleaned_data



class MenuSectionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super(MenuSectionForm, self).__init__(*args, **kwargs)
        
        
        if instance and instance.pk:
            self.fields['sname'].initial = instance.sname

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'sname',
            Submit('submit', 'Submit', css_class='btn-success')
        )

    class Meta:
        model = MenuSection
        fields = ['sname']


class DishForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        instance = kwargs.get('instance')
        super(DishForm, self).__init__(*args, **kwargs)
        
        
        if instance and instance.pk:
            self.fields['section'].queryset = MenuSection.objects.filter(menu__restaurant=instance.section.menu.restaurant)
        elif restaurant:
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


class SeatsForm(forms.ModelForm):
    max_seats = forms.IntegerField(min_value=1, label='Number of People', initial=1)

    class Meta:
        model = Restaurant
        fields = ['max_seats']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'max_seats',
            Submit('submit', 'Submit', css_class='btn btn-success')
        )