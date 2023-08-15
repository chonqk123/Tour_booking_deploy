import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Booking, Rating, Reply
from django.core.validators import MinValueValidator, MaxValueValidator


class TourSearchForm(forms.Form):
    query = forms.CharField(label=_('key search'), max_length=100, required=False)
    min_price = forms.DecimalField(label=_('Minimum Price'), min_value=0, required=False)
    max_price = forms.DecimalField(label=_('Maximum Price'), min_value=0, required=False)
    start_date = forms.DateField(label=_('Start day'), required=False)
    end_date = forms.DateField(label=_('End day'), required=False)
    location = forms.CharField(label=_('Address'), max_length=100, required=False)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['number_of_people', 'departure_date', 'end_date']  # Thêm trường 'end_date' vào form
        widgets = {
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),  # Tùy chỉnh widget cho trường 'end_date'
        }


from django import forms
from .models import Rating, Reply

class RatingForm(forms.ModelForm):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control','placeholder': 'Text goes here!!!','rows':'3','cols':'20'}))
    rating = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        label='Rating',
        help_text='Choose a rating from 1 to 5.'
    )

    class Meta:
        model = Rating
        fields = ['rating', 'content']

class ReplyForm(forms.ModelForm):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control','placeholder': 'Text goes here!!!','rows':'2','cols':'20'}))
    class Meta:
        model = Reply
        fields = ['content']
 

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=255, required=True)
    
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise forms.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9\W]', password):
            raise forms.ValidationError("Mật khẩu phải có ít nhất 3 loại ký tự: chữ thường, viết hoa, số, và ký tự đặc biệt.")
        return password
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class FavoriteTourForm(forms.Form):
    pass
