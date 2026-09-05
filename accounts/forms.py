from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from catalog.models import Fragrance
from .models import Profile, WardrobeItem, UserSettings


class AllUsersPasswordResetForm(PasswordResetForm):
    """
    Override Django's PasswordResetForm to also send reset emails to users
    who signed up via OAuth and have no usable password set.

    Django's default ``get_users()`` filters out users where
    ``has_usable_password()`` is False, which silently prevents OAuth-only
    users from ever setting a password via the "Forgot Password" flow.
    """

    def get_users(self, email):
        active_users = User.objects.filter(
            email__iexact=email,
            is_active=True,
        )
        return (u for u in active_users if u.has_usable_password() or not u.has_usable_password())




class SignupForm(UserCreationForm):
    """New user registration form requiring an email address."""

    email = forms.EmailField(required=True)
    agree_to_terms = forms.BooleanField(
        required=False,
        initial=True,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = True
        if commit:
            user.save()
            Profile.objects.get_or_create(user=user)
        return user


class EditProfileForm(forms.ModelForm):
    """Profile details editor form with dynamic signature fragrance search and email support."""

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'curator@example.com',
            'class': 'form-input',
        })
    )
    favorite_fragrance = forms.ModelChoiceField(
        queryset=Fragrance.objects.none(),
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Profile
        fields = ['display_name', 'bio', 'location', 'avatar_url', 'favorite_fragrance']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'placeholder': 'E.g. Alexander V.',
                'class': 'form-input',
            }),
            'bio': forms.Textarea(attrs={
                'placeholder': 'Share your olfactory sensibilities, favorite houses, or scent memories...',
                'rows': 4,
                'class': 'form-input',
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Paris, France',
                'class': 'form-input',
            }),
            'avatar_url': forms.URLInput(attrs={
                'placeholder': 'https://images.unsplash.com/...',
                'class': 'form-input',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['email'].initial = user.email

        # Dynamically set queryset for favorite_fragrance so validation passes
        # without loading 24,000+ records into memory
        fragrance_ids = []
        if self.instance and self.instance.favorite_fragrance_id:
            fragrance_ids.append(self.instance.favorite_fragrance_id)
        if self.data and self.data.get('favorite_fragrance'):
            try:
                fragrance_ids.append(int(self.data.get('favorite_fragrance')))
            except (ValueError, TypeError):
                pass
        if fragrance_ids:
            self.fields['favorite_fragrance'].queryset = Fragrance.objects.filter(id__in=fragrance_ids)

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if self.user and 'email' in self.cleaned_data:
            new_email = self.cleaned_data.get('email', '').strip()
            if new_email != self.user.email:
                self.user.email = new_email
                self.user.save(update_fields=['email'])
        return profile


class WardrobeItemForm(forms.ModelForm):
    """Form to add or organize a fragrance on a collection shelf."""

    class Meta:
        model = WardrobeItem
        fields = ['fragrance', 'shelf', 'personal_rating', 'bottle_size_ml']
        widgets = {
            'fragrance': forms.Select(attrs={'class': 'form-input'}),
            'shelf': forms.Select(attrs={'class': 'form-input'}),
            'personal_rating': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1, 'max': 5,
                'placeholder': '1-5',
            }),
            'bottle_size_ml': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '100',
            }),
        }


class UserSettingsForm(forms.ModelForm):
    """User preferences editor for MVP."""

    class Meta:
        model = UserSettings
        fields = ['theme', 'profile_visibility', 'default_shelf']
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-input'}),
            'profile_visibility': forms.Select(attrs={'class': 'form-input'}),
            'default_shelf': forms.Select(attrs={'class': 'form-input'}),
        }
        labels = {
            'theme': 'Visual Theme',
            'profile_visibility': 'Profile Visibility',
            'default_shelf': 'Default Wardrobe Shelf',
        }
        help_texts = {
            'theme': 'Choose your preferred visual mode for the Drydown interface.',
            'profile_visibility': 'Control who can view your curator profile and scent activity.',
            'default_shelf': 'The default shelf selected when organizing new fragrances.',
        }


