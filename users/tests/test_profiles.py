import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_user_registration_and_profile_creation():
    client = APIClient()
    response = client.post("/api/auth/register/", {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "StrongPass123"
    }, format="json")
    assert response.status_code == 201
    assert User.objects.filter(username="newuser").exists()
    user = User.objects.get(username="newuser")
    assert hasattr(user, "profile")


@pytest.mark.django_db
def test_follow_unfollow_flow(user_factory):
    u1 = user_factory(username="alice")
    u2 = user_factory(username="bob")
    client = APIClient()
    client.force_authenticate(user=u1)

    # Follow
    res = client.post(f"/api/auth/profiles/{u2.profile.id}/follow/")
    assert res.status_code == 204
    assert u2.followers.filter(follower=u1).exists()

    # Unfollow
    res = client.post(f"/api/auth/profiles/{u2.profile.id}/unfollow/")
    assert res.status_code == 204
    assert not u2.followers.filter(follower=u1).exists()
