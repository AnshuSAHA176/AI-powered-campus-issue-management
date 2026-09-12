
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",include("apps.account.urls")),
    path('complaints/',include('apps.complaint.urls')),
    path('agent/',include('apps.ai_agent.urls')),
    #  path('silk/', include('silk.urls', namespace='silk')),
]

