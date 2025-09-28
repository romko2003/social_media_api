from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from users.models import Follow
from .models import Post, Like, Comment, ScheduledPost
from .serializers import (
    PostSerializer, PostListSerializer, LikeSerializer,
    CommentSerializer, ScheduledPostSerializer
)
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ("list",):
            return PostListSerializer
        return PostSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request
        if request.user.is_authenticated and request.query_params.get("feed"):
            following_ids = Follow.objects.filter(
                follower=request.user
            ).values_list("following_id", flat=True)
            qs = qs.filter(Q(author__in=following_ids) | Q(author=request.user))

        author = request.query_params.get("author")
        if author:
            qs = qs.filter(author__username=author)

        hashtag = request.query_params.get("hashtag")
        if hashtag:
            qs = qs.filter(hashtags__icontains=hashtag.lower())

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(Q(text__icontains=search) | Q(hashtags__icontains=search.lower()))
        return qs

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        Like.objects.get_or_create(user=request.user, post=post)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        Like.objects.filter(user=request.user, post=post).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def liked(self, request):
        qs = Post.objects.filter(likes__user=request.user).select_related("author")
        page = self.paginate_queryset(qs)
        ser = PostListSerializer(page or qs, many=True, context={"request": request})
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == "POST":
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required."}, status=401)
            ser = CommentSerializer(data=request.data, context={"request": request})
            ser.is_valid(raise_exception=True)
            ser.save(author=request.user, post=post)
            return Response(ser.data, status=201)
        qs = post.comments.select_related("author")
        ser = CommentSerializer(qs, many=True)
        return Response(ser.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("author", "post")
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]


class ScheduledPostViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    queryset = ScheduledPost.objects.select_related("author").all()
    serializer_class = ScheduledPostSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            return qs.filter(author=self.request.user)
        return qs.none()
