from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("auctions/<str:filterCriteria>/<str:filterValue>/", views.auctions, name="auctions"),
    path("auction", views.auction, name="auction"),
    path("create", views.create, name="create")

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
