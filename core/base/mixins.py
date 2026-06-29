from django.contrib.auth.mixins import LoginRequiredMixin


class ERPLoginRequiredMixin(LoginRequiredMixin):
    """
    Mixin base para exigir login nas telas do ERP.
    """

    login_url = "login"