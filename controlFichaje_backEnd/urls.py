# PROJECT -> urls.py
# PROJECT -> urls.py (ACTUALIZADO)
#  
from django.contrib import admin
from django.urls import include, path

from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings as django_settings

from fichajeRemoto.api import fichajeRemoto_list, checkserver, validatepin
from django.conf.urls.static import static

MAC_ADDRESS_PATTERN = r'(?P<mac_address>(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2}))'
IP_ADDRESS_PATTERN = r'(?P<ip_address>(?:\d{1,3}\.){3}\d{1,3})'
FW_VERSION_PATTERN = r'(?P<fw_version>(?:\d{1,2}\.){2}\d{1,2})'
HW_VERSION_PATTERN = r'(?P<HW_version>.+)'
PIN_PATTERN = r'(?P<pin>(?:\d{4}\){4})'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Aplicaciones principales
    path("fichajeRemoto/", include("fichajeRemoto.urls")),
    path('fichajeremoto/', include("fichajeRemoto.urls")),  # alias con minúscula
    path("core/", include("core.urls")),
    
    # NUEVA RUTA PARA ADMINISTRACIÓN
    path('administracion/', include('fichajeRemoto.urls_admin')),

    # APIs existentes
    re_path(r'^api/teclados/$',  csrf_exempt(fichajeRemoto_list)   ), 
    re_path(r'^api/%s/checkserver'% MAC_ADDRESS_PATTERN,  csrf_exempt(checkserver)   ),
    re_path(r'^api/%s/validatepin'% MAC_ADDRESS_PATTERN,  csrf_exempt(validatepin)   ),

    path('', include('pwa.urls')),  # Esto expone /manifest.json y /serviceworker.js
]

if django_settings.DEBUG:
        urlpatterns += static(django_settings.MEDIA_URL,
                              document_root=django_settings.MEDIA_ROOT)