import pytest
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()


@pytest.fixture
def user_factory(db):
    def create_user(**kwargs):
        password = kwargs.pop("password", "StrongPass123")
        user = User.objects.create_user(password=password, **kwargs)
        return user
    return create_user


@pytest.fixture
def post_factory(user_factory):
    def create_post(**kwargs):
        author = kwargs.pop("author", user_factory(username="author"))
        return Post.objects.create(author=author, text=kwargs.get("text", "Test post"))
    return create_post
