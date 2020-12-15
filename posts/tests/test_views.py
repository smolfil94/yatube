import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User, Follow
USERNAME = 'NikitaF'
USERNAME2 = 'KrisF'
USERNAME3 = 'Ksu'
SLUG = 'ramax'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group_posts', args=[SLUG])
LOGIN_URL = reverse('login')
PROFILE_URL = reverse('profile', args=[USERNAME])
NEXT_NEW_POST_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'
FOLLOW_URL = reverse('follow_index')
PROFILE_FOLLOW_URL = reverse('profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('profile_unfollow', args=[USERNAME])
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
             )
AUTHOR_PROFILE_URL = reverse('profile', args=[USERNAME2])
AUTHOR_FOLLOW_URL = reverse('profile_follow', args=[USERNAME2])
AUTHOR_UNFOLLOW_URL = reverse('profile_unfollow', args=[USERNAME2])


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=tempfile.gettempdir())
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Ramax Int',
            slug=SLUG
        )
        cls.author = User.objects.create(username=USERNAME2)
        cls.user2 = User.objects.create(username=USERNAME3)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(user=self.user2)
        self.post = Post.objects.create(
            text='Ramax Sys, Ramax int',
            author=self.user,
            group=self.group
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        self.following = Follow.objects.create(
            user=self.user,
            author=self.author
        )
        self.POST_URL = reverse('post', args=[USERNAME, self.post.id])
        self.POST_EDIT_URL = reverse(
            'post_edit',
            args=[USERNAME, self.post.id]
        )
        self.NEXT_POST_EDIT_URL = f'{LOGIN_URL}?next={self.POST_EDIT_URL}'
        self.ADD_COMMENT_URL = reverse('add_comment',
                                       args=[USERNAME, self.post.id])

    def test_pages_show_correct_pagination_in_context(self):
        urls = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
            FOLLOW_URL
        ]
        for url_name in urls:
            with self.subTest():
                cache.clear()
                response = self.authorized_client.get(url_name)
                paginator = response.context.get('paginator')
                self.assertEqual(paginator.num_pages, 1)

    def test_pages_show_correct_post_in_context(self):
        Post.objects.exclude(id=self.post.id).delete()
        Follow.objects.create(user=self.user2, author=self.post.author)
        urls = {
            INDEX_URL: self.authorized_client,
            GROUP_URL: self.authorized_client,
            PROFILE_URL: self.authorized_client,
            self.POST_URL: self.authorized_client,
            FOLLOW_URL: self.authorized_client_2,
        }
        self.post.group = self.group
        self.post.save()
        for url, client in urls.items():
            with self.subTest():
                response = client.get(url)
                if 'page' in response.context:
                    post = response.context['page'][0]
                else:
                    post = response.context['post']
                self.assertEqual(post, self.post)

    def test_author_correct_context(self):
        urls = [
            PROFILE_URL,
            self.POST_URL
        ]
        for url in urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                author = response.context['author']
                self.assertEqual(author, self.user)

    def test_group_correct_context(self):
        response = self.authorized_client.get(GROUP_URL)
        group = response.context['group']
        self.assertEqual(group, self.group)

    def test_group_detail_page_dont_show_post_without_group(self):
        self.post.group = None
        self.post.save()
        response = self.authorized_client.get(GROUP_URL)
        page = response.context['page']
        self.assertEqual(len(page), 0)

    def test_pages_show_image_in_context(self):
        Post.objects.exclude(id=self.post.id).delete()
        Follow.objects.create(user=self.user2, author=self.post.author)
        urls = {
            INDEX_URL: self.authorized_client,
            GROUP_URL: self.authorized_client,
            PROFILE_URL: self.authorized_client,
            self.POST_URL: self.authorized_client,
            FOLLOW_URL: self.authorized_client_2,
        }
        self.post.image = self.uploaded
        self.post.group = self.group
        self.post.save()
        for url, client in urls.items():
            with self.subTest():
                response = client.get(url)
                if 'page' in response.context:
                    post = response.context['page'][0]
                else:
                    post = response.context['post']
                self.assertIsNotNone(post.image)

    def test_page_cache_on_page(self):
        response = self.authorized_client.get(INDEX_URL)
        content = response.content
        self.assertEqual(response.content, content)
        Post.objects.create(
            text='Хочу подписаться на Р.Киплинга',
            author=self.user,
        )
        response = self.authorized_client.get(INDEX_URL)
        self.assertEqual(response.content, content)
        cache.clear()
        response = self.authorized_client.get(INDEX_URL)
        self.assertNotEqual(response.content, content)

    def test_authorized_user_can_follow_author(self):
        Follow.objects.all().delete()
        self.assertFalse(Follow.objects.exists())
        response = self.authorized_client.get(AUTHOR_FOLLOW_URL,
                                              follow=True)
        self.assertRedirects(response, AUTHOR_PROFILE_URL)
        following = Follow.objects.filter(
            user=self.user, author=self.author
        ).exists()
        self.assertTrue(following)

    def test_authorized_user_can_see_followed_author_post(self):
        Post.objects.all().delete()
        post = Post.objects.create(
            text='Хочу подписаться на Р.Киплинга',
            author=self.author
        )
        response = self.authorized_client.get(FOLLOW_URL)
        post_at_page = response.context['page'][0]
        self.assertEqual(post_at_page, post)

    def test_authorized_user_can_unfollow_author(self):
        self.assertTrue(Follow.objects.exists())
        response = self.authorized_client.get(AUTHOR_UNFOLLOW_URL,
                                              follow=True)
        self.assertRedirects(response, AUTHOR_PROFILE_URL)
        self.assertFalse(Follow.objects.exists())

    def test_authorized_user_doesnt_see_unfollowed_author_post(self):
        Follow.objects.all().delete()
        Post.objects.create(
            text='Хочу подписаться на Р.Киплинга',
            author=self.author
        )
        response = self.authorized_client.get(FOLLOW_URL)
        self.assertEqual(len(response.context['page']), 0)
