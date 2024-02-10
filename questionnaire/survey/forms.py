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

    def __init__(self, *args, **kwargs):
        options = kwargs.pop('options', None)
        super(QuestionResponseForm, self).__init__(*args, **kwargs)

        if options:
            self.fields['selected_option'] = forms.ChoiceField(
                choices=options,
                widget=forms.RadioSelect,
                label='Выберите вариант ответа'
            )
