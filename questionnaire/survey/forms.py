from django import forms


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True, label='Email')


class LoginForm(forms.Form):
    email = forms.EmailField(required=True, label='Email')
    password = forms.CharField(widget=forms.PasswordInput())
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), label='Remember me')


class QuestionResponseForm(forms.Form):
    selected_option = forms.ChoiceField(choices=[('1', 'Первый вариант'), ('2', 'Второй вариант'), ('3', 'Третий вариант'), ('4', 'Четвертый вариант')], widget=forms.RadioSelect, label='Выберите вариант ответа')
