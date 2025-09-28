import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_create_post(user_factory):
    user = user_factory(username="poster")
    client = APIClient()
    client.force_authenticate(user=user)
    res = client.post("/api/posts/", {"text": "Hello #world"})
    assert res.status_code == 201
    data = res.json()
    assert "world" in data["hashtags"]


@pytest.mark.django_db
def test_like_and_unlike_post(user_factory, post_factory):
    user = user_factory(username="liker")
    post = post_factory(text="Like me!")
    client = APIClient()
    client.force_authenticate(user=user)

    # Like
    res = client.post(f"/api/posts/{post.id}/like/")
    assert res.status_code == 204
    assert post.likes.filter(user=user).exists()

    # Unlike
    res = client.post(f"/api/posts/{post.id}/unlike/")
    assert res.status_code == 204
    assert not post.likes.filter(user=user).exists()


@pytest.mark.django_db
def test_comment_on_post(user_factory, post_factory):
    user = user_factory(username="commenter")
    post = post_factory()
    client = APIClient()
    client.force_authenticate(user=user)
    res = client.post(f"/api/posts/{post.id}/comments/", {"text": "Nice post!"})
    assert res.status_code == 201
    assert post.comments.filter(author=user, text="Nice post!").exists()
