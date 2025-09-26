from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, ScheduledPostViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("comments", CommentViewSet, basename="comment")
router.register("scheduled-posts", ScheduledPostViewSet, basename="scheduled-post")

urlpatterns = [
    path("", include(router.urls)),
]
