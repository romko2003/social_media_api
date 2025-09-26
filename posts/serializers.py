import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Post, Like, Comment, ScheduledPost

User = get_user_model()
HASHTAG_RE = re.compile(r"#(\w+)")


def extract_hashtags(text: str) -> list[str]:
    return sorted({m.group(1).lower() for m in HASHTAG_RE.finditer(text or "")})


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class CommentSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "text", "created_at")


class PostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "author", "text", "image", "hashtags",
                  "likes_count", "comments_count", "created_at")
        read_only_fields = ("hashtags",)

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["author"] = request.user
        validated_data["hashtags"] = extract_hashtags(validated_data.get("text", ""))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "text" in validated_data:
            validated_data["hashtags"] = extract_hashtags(validated_data.get("text", ""))
        return super().update(instance, validated_data)


class PostListSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        fields = ("id", "author", "text", "image", "hashtags",
                  "likes_count", "comments_count", "created_at")


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")
        read_only_fields = ("user",)


class ScheduledPostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)

    class Meta:
        model = ScheduledPost
        fields = ("id", "author", "text", "image", "publish_at", "processed", "created_at")

    def validate_publish_at(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("publish_at має бути в майбутньому")
        return value

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
