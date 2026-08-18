from rest_framework.routers import DefaultRouter

from .api import LayoutViewSet

router = DefaultRouter()
router.register("layouts", LayoutViewSet, basename="layout")

urlpatterns = router.urls
