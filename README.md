# MCDA_API

## DJ_Rest_Auth

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
- /api/v1/auth/registration/verify-email/ - dj_rest_auth.registration.views.VerifyEmailView rest_verify_email
