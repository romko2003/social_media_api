from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


def image_upload_path(instance, filename):
    return f"posts/{instance.author_id}/{filename}"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    text = models.TextField(max_length=2000)
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    hashtags = models.JSONField(default=list, blank=True)  # збережені #теги
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Post({self.id}) by {self.author}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class ScheduledPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scheduled_posts")
    text = models.TextField(max_length=2000)
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    publish_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def should_publish(self) -> bool:
        return (not self.processed) and self.publish_at <= timezone.now()
