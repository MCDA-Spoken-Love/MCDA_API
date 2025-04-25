from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from auth_app.models import Users


class AppUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Users
        fields = UserCreationForm.Meta.fields + \
            ('password', 'email', 'gender', 'sexuality', 'connection_code',)


class AppUserLoginForm(AuthenticationForm):
    # Add any additional form fields if required
    pass
