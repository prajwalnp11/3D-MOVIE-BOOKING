from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=100, required=False, initial='Kochi')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=commit)
        phone = self.cleaned_data.get('phone', '')
        city = self.cleaned_data.get('city', 'Kochi')
        if hasattr(user, 'profile'):
            user.profile.phone = phone
            user.profile.city = city
            user.profile.save()
        else:
            Profile.objects.create(user=user, phone=phone, city=city)
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'city', 'avatar']
