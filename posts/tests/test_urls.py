from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'NikitaF'
SLUG = 'ramax'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group_posts', args=[SLUG])
LOGIN_URL = reverse('login')
PROFILE_URL = reverse('profile', args=[USERNAME])
AUTHOR_URL = reverse('about')
SPEC_URL = reverse('terms')
NEXT_NEW_POST_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'
ABOUT_AUTHOR_URL = f'/about{AUTHOR_URL}'
ABOUT_SPEC_URL = f'/about{SPEC_URL}'
FOLLOW_URL = reverse('follow_index')


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Ramax Int',
            slug=SLUG
        )
        cls.post = Post.objects.create(
            text='Ramax Sys, Ramax int',
            author=cls.user,
        )
        site = Site.objects.get(pk=1)
        flat_about = FlatPage.objects.create(
            url=AUTHOR_URL,
            title='Об авторе',
            content='<b>content</b>'
        )
        flat_tech = FlatPage.objects.create(
            url=SPEC_URL,
            title='Технологии',
            content='<b>content</b>'
        )
        flat_about.sites.add(site)
        flat_tech.sites.add(site)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.POST_URL = reverse('post', args=[USERNAME, self.post.id])
        self.POST_EDIT_URL = reverse(
            'post_edit',
            args=[USERNAME, self.post.id]
        )
        self.NEXT_POST_EDIT_URL = f'{LOGIN_URL}?next={self.POST_EDIT_URL}'

    def test_flatpages_exist_at_desired_location(self):
        flatpages_urls_names = [ABOUT_AUTHOR_URL, ABOUT_SPEC_URL]
        for url in flatpages_urls_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_pages_urls_exist_at_desired_location(self):
        urls = [
            INDEX_URL,
            GROUP_URL,
            NEW_POST_URL,
            PROFILE_URL,
            self.POST_URL,
            self.POST_EDIT_URL,
            FOLLOW_URL,
        ]
        for url in urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_create_new_post_url_redirect_anonymous(self):
        count = Post.objects.count()
        response = self.guest_client.get(NEW_POST_URL, follow=True)
        self.assertRedirects(response, NEXT_NEW_POST_URL)
        self.assertEqual(Post.objects.count(), count)

    def test_post_edit_url_redirect_anonymous(self):
        count = Post.objects.count()
        response = self.guest_client.get(self.POST_EDIT_URL, follow=True)
        self.assertRedirects(response, self.NEXT_POST_EDIT_URL)
        self.assertEqual(Post.objects.count(), count)

    def test_post_edit_url_redirect_non_author(self):
        count = Post.objects.count()
        non_author = User.objects.create(username='non_author')
        self.authorized_client.force_login(non_author)
        response = self.authorized_client.get(self.POST_EDIT_URL, follow=True)
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(Post.objects.count(), count)

    def test_urls_use_correct_templates(self):
        urls = {
            INDEX_URL: 'index.html',
            GROUP_URL: 'group.html',
            NEW_POST_URL: 'new_post.html',
            self.POST_EDIT_URL: 'new_post.html',
            PROFILE_URL: 'profile.html',
            self.POST_URL: 'post.html',
            FOLLOW_URL: 'follow.html',
        }
        for url, template in urls.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_not_found(self):
        response = self.guest_client.get('/test/')
        self.assertEqual(response.status_code, 404)
