from django import forms


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True, label='Email')


class LoginForm(forms.Form):
    email = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), label='Remember me')