from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, WardrobeItem


class SignupForm(UserCreationForm):
    """New user registration form requiring an email address."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user)
        return user


class EditProfileForm(forms.ModelForm):
    """Profile details editor form."""

    class Meta:
        model = Profile
        fields = ['display_name', 'bio', 'avatar_url', 'location', 'favorite_fragrance']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'placeholder': 'Display name',
                'class': 'form-input rounded-lg',
            }),
            'bio': forms.Textarea(attrs={
                'placeholder': 'Share your scent story and preferences...',
                'rows': 3,
                'class': 'form-input rounded-lg',
            }),
            'avatar_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/avatar.jpg',
                'class': 'form-input rounded-lg',
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'City, Country',
                'class': 'form-input rounded-lg',
            }),
            'favorite_fragrance': forms.Select(attrs={
                'class': 'form-input rounded-lg',
            }),
        }


class WardrobeItemForm(forms.ModelForm):
    """Form to add or organize a fragrance on a collection shelf."""

    class Meta:
        model = WardrobeItem
        fields = ['fragrance', 'shelf', 'personal_rating', 'bottle_size_ml']
        widgets = {
            'fragrance': forms.Select(attrs={'class': 'form-input rounded-lg'}),
            'shelf': forms.Select(attrs={'class': 'form-input rounded-lg'}),
            'personal_rating': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'min': 1, 'max': 5,
                'placeholder': '1-5',
            }),
            'bottle_size_ml': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'placeholder': '100',
            }),
        }

