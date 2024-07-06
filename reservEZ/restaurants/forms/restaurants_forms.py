from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, Submit
from ..models import Reservation, ActiveOrderItem, Restaurant, Tag
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum




class ReservationForm(forms.ModelForm):
    weekday = forms.ChoiceField(label='Day')
    time = forms.TimeField(widget=forms.Select())
    number_of_people = forms.IntegerField(min_value=1, label='Number of People', initial=1)

    class Meta:
        model = Reservation
        fields = ['weekday', 'time', 'number_of_people']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Make a Reservation',
                Div(
                    Div('weekday', css_class='col-md-6'),
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

        
        today = timezone.now().date()
        days = []
        for i in range(7):
            day = today + timedelta(days=i)
            weekday_display = day.strftime('%A (%d/%m/%Y)')
            weekday_value = day.strftime('%Y-%m-%d')
            if self.restaurant.opening_hours.filter(weekday=day.weekday()).exists():
                days.append((weekday_value, weekday_display))
        self.fields['weekday'].choices = days

    def clean(self):
        cleaned_data = super().clean()
        date_str = cleaned_data.get('weekday')
        time = cleaned_data.get('time')
        number_of_people = cleaned_data.get('number_of_people')

        if date_str and time:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            weekday = date.weekday()
            opening_hours = self.restaurant.opening_hours.filter(weekday=weekday).first()
            if not opening_hours:
                raise forms.ValidationError('The restaurant is closed on this day.')

            opening_time = datetime.combine(date, opening_hours.opening_time)
            closing_time = datetime.combine(date, opening_hours.closing_time)
            reservation_time = datetime.combine(date, time)

            if not (opening_time <= reservation_time <= closing_time):
                raise forms.ValidationError('The reservation time is outside the opening hours.')

            
            if Reservation.objects.filter(restaurant=self.restaurant, user=self.user, date=date).exists():
                raise forms.ValidationError('You can only make one reservation per day at this restaurant.')

            
            total_reserved_seats = Reservation.objects.filter(restaurant=self.restaurant, date=date).aggregate(total_seats=Sum('number_of_people'))['total_seats']
            if total_reserved_seats is None:
                total_reserved_seats = 0
            available_seats = self.restaurant.max_seats - total_reserved_seats
            if number_of_people > available_seats:
                raise forms.ValidationError('There are no available seats for this time slot.')

            
            cleaned_data['date'] = date

        return cleaned_data


class RestaurantForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'address', 'tags']

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if tags.count() > 3:
            raise forms.ValidationError("You can select a maximum of 3 tags.")
        return tags


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = ActiveOrderItem
        fields = ['quantity']