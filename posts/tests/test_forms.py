import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, User, Group, Comment

USERNAME = 'NikitaF'
SLUG = 'ramax'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group_posts', args=[SLUG])
LOGIN_URL = reverse('login')
PROFILE_URL = reverse('profile', args=[USERNAME])
NEXT_NEW_POST_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=tempfile.gettempdir())
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Ramax Int',
            slug=SLUG
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
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
        self.POST_URL = reverse('post', args=[USERNAME, self.post.id])
        self.POST_EDIT_URL = reverse(
            'post_edit',
            args=[USERNAME, self.post.id]
        )
        self.NEXT_POST_EDIT_URL = f'{LOGIN_URL}?next={self.POST_EDIT_URL}'
        self.ADD_COMMENT_URL = reverse('add_comment',
                                       args=[USERNAME, self.post.id])

    def test_create_post(self):
        Post.objects.all().delete()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        data_source = {
            'text': 'test string',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=data_source,
            follow=True
        )
        page = response.context['page']
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(len(page), 1)
        created_post = page[0]
        self.assertEqual(created_post.text, data_source['text'])
        self.assertEqual(created_post.group, self.group)
        self.assertEqual(created_post.author, self.user)
        self.assertIsNotNone(created_post.image)

    def test_edit_post(self):
        group = Group.objects.create(
            title='new_test',
            description='new_test',
            slug='new_test-slag'
        )
        data_source = {
            'text': 'ramax',
            'group': group.id,
            'uploaded': self.uploaded
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=data_source,
            follow=True
        )
        self.assertRedirects(response, self.POST_URL)
        edited_post = response.context.get('post')
        self.assertEqual(edited_post.text, data_source['text'])
        self.assertEqual(edited_post.group, group)
        self.assertEqual(edited_post.author, self.user)
        self.assertIsNotNone(edited_post.image)

    def test_title_label(self):
        text_label = self.form.fields['text'].label
        self.assertEqual(text_label, 'Текст')

    def test_new_post_page_show_correct_context(self):
        response = self.authorized_client.get(NEW_POST_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            form_field = response.context.get('form').fields.get(value)
            self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(self.POST_EDIT_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            form_field = response.context.get('form').fields.get(value)
            self.assertIsInstance(form_field, expected)

    def test_create_comment(self):
        form_data = {
            'text': 'Текст комментария!',
            'author': self.user
        }
        self.assertEqual(Comment.objects.count(), 0)
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, self.POST_URL)
        comment = response.context.get('comments')[0]
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, form_data['author'])

    def test_create_comment_anonymous(self):
        count_comments = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария!'
        }
        response = self.guest_client.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), count_comments)
        comment_redirect_url = f'{LOGIN_URL}?next={self.ADD_COMMENT_URL}'
        self.assertRedirects(response, comment_redirect_url)
        self.assertFalse(Comment.objects.exists())

    def test_create_new_post_url_redirect_anonymous_post(self):
        group = Group.objects.create(
            title='new_test',
            description='new_test',
            slug='new_test-slag'
        )
        data_source = {
            'text': 'ramax',
            'group': group.id,
        }
        count = Post.objects.count()
        response = self.guest_client.post(
            NEW_POST_URL,
            data=data_source,
            follow=True
        )
        self.assertRedirects(response, NEXT_NEW_POST_URL)
        edited_post = response.context.get('post')
        self.assertEqual(Post.objects.count(), count)
        self.assertEqual(Post.objects.last(), self.post)

    def test_post_edit_url_redirect_anonymous_post(self):
        group = Group.objects.create(
            title='new_test',
            description='new_test',
            slug='new_test-slag'
        )
        data_source = {
            'text': 'ramax',
            'group': group.id,
        }
        count = Post.objects.count()
        response = self.guest_client.post(
            self.POST_EDIT_URL,
            data=data_source,
            follow=True
        )
        self.assertRedirects(response, self.NEXT_POST_EDIT_URL)
        self.assertEqual(Post.objects.count(), count)
        self.assertEqual(Post.objects.last(), self.post)
