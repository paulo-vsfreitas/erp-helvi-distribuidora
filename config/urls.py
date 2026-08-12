from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.auth_views import HelviLoginView

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "senha/login/",
        HelviLoginView.as_view(),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),

    path("senha/", include("django.contrib.auth.urls")),

    path("", include("core.urls")),
    path("clientes/", include("clientes.urls")),
    path("catalogo/", include("catalogo.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("fornecedores/", include("fornecedores.urls")),
    path("produtos/", include("produtos.urls")),
    path("estoque/", include("estoque.urls")),
    path("compras/", include("compras.urls")),
    path("financeiro/", include("financeiro.urls")),
    path("comercial/", include("comercial.urls")),
    path("vendas/", include("vendas.urls")),
    path("configuracoes/", include("configuracoes.urls")),


]

if settings.DEBUG or getattr(settings, "APP_ENV", "production") in {"development", "staging"}:
    # Em desenvolvimento e homologacao os uploads precisam ser servidos pelo
    # proprio Django para permitir a conferencia visual de catalogos/produtos.
    # Producao continua dependendo de storage/web server apropriado.
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
