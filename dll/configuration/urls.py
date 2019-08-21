"""dll URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from dll.content.views import HomePageView, ImprintView, DataPrivacyView, StructureView, UsageView, DevelopmentView, \
    NewsletterRegisterView, NewsletterUnregisterView, ContactView, ToolDetailView, TrendDetailView, \
    TeachingModuleDetailView, CompetenceFilterView, TeachingModuleFilterView, \
    TeachingModuleDataFilterView, ToolDataFilterView, TrendFilterView, ToolFilterView, TrendDataFilterView, \
    PublishedContentViewSet, DraftsContentViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'inhalte', PublishedContentViewSet, base_name='public-content')
router.register(r'inhalt-bearbeiten', DraftsContentViewSet, base_name='draft-content')
router.register(r'review', ReviewViewSet, base_name='review')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('impressum', ImprintView.as_view(), name='imprint'),
    path('datenschutz', DataPrivacyView.as_view(), name='data-privacy'),
    path('struktur', StructureView.as_view(), name='structure'),
    path('nutzung', UsageView.as_view(), name='usage'),
    path('entwicklung', DevelopmentView.as_view(), name='development'),
    path('newsletter', NewsletterRegisterView.as_view(), name='newsletter'),
    path('newsletter/abmelden', NewsletterUnregisterView.as_view(), name='newsletter-unregister'),
    path('kontakt', ContactView.as_view(), name='contact'),
    path('kontakt', ContactView.as_view(), name='contact-form'),  # todo: remove this. just for avoiding immense bug stacktraces from reverse error
    path('faq', views.flatpage, {'url': '/faq/'}, name='faq'),
    path('tools/<slug:slug>', ToolDetailView.as_view(), name='tool-detail'),
    path('trends/<slug:slug>', TrendDetailView.as_view(), name='trend-detail'),
    path('unterrichtsbausteine/<slug:slug>', TeachingModuleDetailView.as_view(), name='teaching-module-detail'),
    path('kompetenz/<slug:slug>', CompetenceFilterView.as_view(), name='competence-filter'),
    path('unterrichtsbausteine', TeachingModuleFilterView.as_view(), name='teaching-modules-filter'),
    path('tools', ToolFilterView.as_view(), name='tools-filter'),
    path('trends', TrendFilterView.as_view(), name='trends-filter'),
    path('', include('dll.user.urls', namespace='user')),
    # path('', include('django.contrib.flatpages.urls')),
    path('api/', include(router.urls)),
    path('api/unterrichtsbausteine', TeachingModuleDataFilterView.as_view(), name='teaching-modules-data-filter'),
    path('api/tools', ToolDataFilterView.as_view(), name='tools-data-filter'),
    path('api/trends', TrendDataFilterView.as_view(), name='trends-data-filter'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
