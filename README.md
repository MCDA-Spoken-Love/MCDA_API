# MCDA_API

<!-- ## DJ_Rest_Auth

### Existing Endpoints

- /api/v1/auth/login/ - dj_rest_auth.views.LoginView rest_login
- /api/v1/auth/logout/ - dj_rest_auth.views.LogoutView rest_logout
- /api/v1/auth/password/change/ - dj_rest_auth.views.PasswordChangeView rest_password_change
- /api/v1/auth/password/reset/ - dj_rest_auth.views.PasswordResetView rest_password_reset
- /api/v1/auth/password/reset/confirm/ - dj_rest_auth.views.PasswordResetConfirmView rest_password_reset_confirm
- /api/v1/auth/token/refresh/ - dj_rest_auth.jwt_auth.RefreshViewWithCookieSupport token_refresh
- /api/v1/auth/token/verify/ - rest_framework_simplejwt.views.TokenVerifyView token_verify
- /api/v1/auth/user/ - dj_rest_auth.views.UserDetailsView rest_user_details
- /api/v1/auth/registration/ - dj_rest_auth.registration.views.RegisterView rest_register
- /api/v1/auth/registration/account-confirm-email/<key>/ - django.views.generic.base.TemplateView account_confirm_email
- /api/v1/auth/registration/account-email-verification-sent/ - django.views.generic.base.TemplateView account_email_verification_sent
- /api/v1/auth/registration/resend-email/ - dj_rest_auth.registration.views.ResendEmailVerificationView rest_resend_email
- /api/v1/auth/registration/verify-email/ - dj_rest_auth.registration.views.VerifyEmailView rest_verify_email -->

## How to run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up environment variables

Create a `.env` file in the project root and add your secrets and database config:

```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_USER_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
USER_TOKEN=your_api_token
```

### 3. Start Redis (for WebSocket support)

Make sure Redis is installed. Start it with:

```bash
redis-server
```

### 4. Run Django migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

### 6. Start Daphne for WebSocket support

Activate your virtual environment and run:

```bash
source venv/bin/activate
daphne mcda_api_project.asgi:application
```

### 7. Run tests

```bash
pytest
```

### 8. WebSocket testing

You can use `test_ws.py` to test WebSocket connections. Make sure your `.env` file contains a valid `USER_TOKEN`.

```bash
python test_ws.py
```

---

### 9. Create a user token for WebSocket/API authentication

To create a token for a user, run the following in the Django shell:

```bash
python manage.py shell
```

Then, in the shell:

```python
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
User = get_user_model()
user = User.objects.get(username="your_username")  # Replace with your username
token, created = Token.objects.get_or_create(user=user)
print(token.key)
```

Copy the token and use it in your `.env` or client code for authenticated WebSocket/API requests.

**Note:**

- For production, configure your database, secrets, and allowed hosts securely.
- Redis is required for Django Channels group messaging and multi-process support.
- Daphne is required for WebSocket support.
