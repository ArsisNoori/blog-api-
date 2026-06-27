from django.shortcuts import render, redirect
from django.views import generic
from .forms import UserRegisterForm
from django.urls import reverse_lazy, reverse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.models import User

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from .tokens import token_generator
from accounts.tokens import token_generator

# Create your views here.

class UserRegisterView(generic.CreateView):
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)

        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = token_generator.make_token(user)

        activation_link = (
            f'http://127.0.0.1:8000/accounts/activate/'
            f'{uid}/{token}/'
        )


        send_mail(
            subject='فعال سازی حساب',
            message=activation_link,
            from_email=None,
            recipient_list=[user.email]
        )

        return redirect('accounts:user_login')


class ActivateAccountView(View):

    def get(self, request, uidb64, token):

        try:
            uid = force_str(
                urlsafe_base64_decode(uidb64)
            )
            user = User.objects.get(pk=uid)

            print("user:", user.username)

        except Exception as e:
            user = None
        if (user is not None
                and token_generator.check_token(user, token)):

            user.is_active = True
            user.save()

            return redirect('accounts:user_login')
        return redirect('accounts:user_login')