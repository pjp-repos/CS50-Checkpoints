"""wiki URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Path para app de administración del sitio... Viene por default, para cuando el usuario ponga www.elsitioelSitioQueSea.com/admin/
    path('admin/', admin.site.urls),
    # Agrego al proyecto, las urls que puse en el archivo de URLS propio de la app
    path( 'wiki/', include("encyclopedia.urls"))
]
