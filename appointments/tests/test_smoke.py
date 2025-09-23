import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_homepage_ok(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200
