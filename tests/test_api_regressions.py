from http import HTTPStatus

import pytest


@pytest.mark.django_db
def test_optional_post_pagination(client, post, post_2):
    url = '/api/v1/posts/'
    response = client.get(url)
    assert isinstance(response.json(), list)

    response = client.get(url, {'limit': 1, 'offset': 1})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert data['results'][0]['id'] == post.id
    assert data['previous'] is not None
    assert data['next'] is None


@pytest.mark.django_db
@pytest.mark.parametrize('method', ['get', 'put', 'patch', 'delete'])
def test_comment_must_belong_to_post(
    user_client, post, another_post, comment_1_post, method,
):
    url = (
        f'/api/v1/posts/{another_post.id}/comments/{comment_1_post.id}/'
    )
    response = getattr(user_client, method)(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_comments_of_missing_post(client, user_client):
    url = '/api/v1/posts/999/comments/'
    assert client.get(url).status_code == HTTPStatus.NOT_FOUND
    response = user_client.post(url, {'text': 'Комментарий'})
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_comment_cannot_be_moved(
    user_client, post, another_post, comment_1_post,
):
    url = f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/'
    response = user_client.patch(
        url, {'post': another_post.id, 'text': 'Обновлённый комментарий'},
    )
    assert response.status_code == HTTPStatus.OK
    comment_1_post.refresh_from_db()
    assert comment_1_post.post == post
