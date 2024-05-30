from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, Submit
from ..models import Reservation, ActiveOrderItem
from django.utils import timezone
from datetime import datetime, timedelta

class ReservationForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    number_of_people = forms.IntegerField(min_value=1, label='Number of People')

    class Meta:
        model = Reservation
        fields = ['date', 'time', 'number_of_people']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Make a Reservation',
                Div(
                    Div('date', css_class='col-md-6'),
                    Div('time', css_class='col-md-6'),
                    css_class='row'
                ),
                Div(
                    Div('number_of_people', css_class='col-md-12'),
                    css_class='row'
                ),
            ),
            Submit('submit', 'Submit'),
        )

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            # Check if reservation time is within opening hours
            weekday = date.weekday()
            opening_hours = self.restaurant.opening_hours.filter(weekday=weekday).first()
            if not opening_hours:
                raise forms.ValidationError('The restaurant is closed on this day.')

            opening_time = datetime.combine(date, opening_hours.opening_time)
            closing_time = datetime.combine(date, opening_hours.closing_time)
            reservation_time = datetime.combine(date, time)

            if not (opening_time <= reservation_time <= closing_time):
                raise forms.ValidationError('The reservation time is outside the opening hours.')

            # Check if the user has already made a reservation for this day at the same restaurant
            if Reservation.objects.filter(restaurant=self.restaurant, user=self.user, date=date).exists():
                raise forms.ValidationError('You can only make one reservation per day at this restaurant.')

        return cleaned_data


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = ActiveOrderItem
        fields = ['quantity']