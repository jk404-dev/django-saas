from django import forms
from allauth.account.forms import LoginForm, SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

class BootstrapLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'login-form'
        self.helper.form_method = 'post'
        
        # Apply Bootstrap classes to fields
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'
        
        # Explicitly add the submit button - this is key!
        self.helper.add_input(Submit('submit', 'Sign In', css_class='btn btn-primary w-100 mt-3'))

class BootstrapSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'signup-form'
        self.helper.form_method = 'post'
        
        # Apply Bootstrap classes to fields
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'
        
        # Explicitly add the submit button
        self.helper.add_input(Submit('submit', 'Sign Up', css_class='btn btn-primary w-100 mt-3'))