from django.contrib.auth.mixins import PermissionRequiredMixin


class ERPPermissionMixin(PermissionRequiredMixin):
    """
    Mixin base para controle de permissões do ERP.
    """

    raise_exception = True