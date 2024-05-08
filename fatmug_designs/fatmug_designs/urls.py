# urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin site URL.
    path('admin/', admin.site.urls),

    # Include app-specific URLs under the "api/" namespace.
    path("api/", include("fatmug_app.urls")),
]
