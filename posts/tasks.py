from celery import shared_task
from django.utils import timezone
from .models import ScheduledPost, Post


@shared_task
def publish_scheduled_posts():
    to_publish = ScheduledPost.objects.filter(processed=False, publish_at__lte=timezone.now())
    created_ids = []
    for item in to_publish:
        post = Post.objects.create(
            author=item.author,
            text=item.text,
            image=item.image,        # зауваження: у продакшн краще копіювати файл
            hashtags=[],             # будуть перераховані в serializer при класичному створенні
        )
        item.processed = True
        item.save(update_fields=["processed"])
        created_ids.append(post.id)
    return created_ids
