import test_mocks  # noqa: F401 – installs third-party stubs before Django loads

from django.contrib.auth.models import User
from django.test import TestCase, Client

from pages.models import Post


def make_staff_user(username='editor'):
    return User.objects.create_user(username=username, password='pass1234', is_staff=True)


def make_post(author=None, title='Test Post', category='N'):
    if author is None:
        author = make_staff_user()
    return Post.objects.create(title=title, body='Some content here.', author=author, category=category)


class PostModelTest(TestCase):
    def test_str(self):
        post = make_post()
        self.assertEqual(str(post), 'Test Post')

    def test_category_choices(self):
        author = make_staff_user()
        post_news = Post.objects.create(title='News', body='x', author=author, category='N')
        post_review = Post.objects.create(title='A Review', body='x', author=author, category='R')
        self.assertEqual(post_news.get_category_display(), 'News')
        self.assertEqual(post_review.get_category_display(), 'Reviews')


class NewsFeedTest(TestCase):
    def test_rss_feed_accessible(self):
        response = Client().get('/rss/')
        self.assertEqual(response.status_code, 200)

    def test_rss_feed_with_posts(self):
        author = make_staff_user()
        Post.objects.create(title='News Item 1', body='content', author=author, category='N')
        Post.objects.create(title='News Item 2', body='content', author=author, category='N')
        response = Client().get('/rss/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('News Item 1', content)
        self.assertIn('News Item 2', content)

    def test_rss_feed_only_shows_news_category(self):
        author = make_staff_user()
        Post.objects.create(title='News Only', body='content', author=author, category='N')
        Post.objects.create(title='Review Only', body='content', author=author, category='R')
        response = Client().get('/rss/')
        content = response.content.decode()
        self.assertIn('News Only', content)
        self.assertNotIn('Review Only', content)


