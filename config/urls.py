from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "senha/login/",
        auth_views.LoginView.as_view(
            template_name="core/login.html"
        ),
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


]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )