from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, Follow
from .serializers import (
    RegisterSerializer, ProfileSerializer, ProfileUpdateSerializer,
    FollowSerializer, UserPublicSerializer
)
from .permissions import IsSelfProfile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            # якщо токен не валідний або відсутній — просто 204
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list: Пошук/перегляд профілів (?search=username/bio/email)
    retrieve: Перегляд чужого профілю
    me: Перегляд/оновлення мого профілю
    follow/unfollow: Дії підписки
    followers/following: Списки
    """
    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = []
    search_fields = []

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(user__username__icontains=search)
                | Q(bio__icontains=search)
                | Q(user__email__icontains=search)
            )
        return qs

    @action(detail=False, methods=["get", "patch"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        profile = request.user.profile
        if request.method == "PATCH":
            ser = ProfileUpdateSerializer(profile, data=request.data, partial=True)
            ser.is_valid(raise_exception=True)
            ser.save()
        ser = ProfileSerializer(profile)
        return Response(ser.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, pk=None):
        target = self.get_object().user
        if target == request.user:
            return Response({"detail": "Неможливо підписатися на себе."}, status=400)
        Follow.objects.get_or_create(follower=request.user, following=target)
        return Response(status=204)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, pk=None):
        target = self.get_object().user
        Follow.objects.filter(follower=request.user, following=target).delete()
        return Response(status=204)

    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        user = self.get_object().user
        qs = user.followers.select_related("follower").all()
        data = [{"id": f.follower.id, "username": f.follower.username} for f in qs]
        return Response(data)

    @action(detail=True, methods=["get"])
    def following(self, request, pk=None):
        user = self.get_object().user
        qs = user.following.select_related("following").all()
        data = [{"id": f.following.id, "username": f.following.username} for f in qs]
        return Response(data)
