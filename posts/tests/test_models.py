from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='NikitaF'
        )
        Post.objects.create(
            text='A'*300,
            author=cls.user
        )
        cls.post = Post.objects.first()

    def test_field_labels(self):
        post = self.post
        verbose_names = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        with self.subTest():
            for field, verbose_name in verbose_names.items():
                verbose = post._meta.get_field(field).verbose_name
                self.assertEqual(verbose, verbose_name)

    def test_text_help_text(self):
        post = self.post
        help_texts = {
            'text': 'Введите текст записи',
            'group': 'При необходимости укажите сообщество',
        }
        with self.subTest():
            for field, help_text in help_texts.items():
                text = post._meta.get_field(field).help_text
                self.assertEqual(text, help_text)

    def test_object_name_is_title_field(self):
        post = self.post
        text = post.text[:15]
        expected_text = f'{text}... Автор: {post.author}. Дата: {post.pub_date}'
        self.assertEqual(expected_text, str(post), 'ошибка')


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NikitaF')
        Group.objects.create(
            title='Тестовое название',
            slug='test-name',
            description='Тестовое описание',
        )
        cls.group = Group.objects.first()

    def test_fields_labels(self):
        group = GroupModelTest.group
        verbose_names = {
            'title': 'Заголовок',
            'slug': 'Ключ',
            'description': 'Описание',
        }
        with self.subTest():
            for field, verbose_name in verbose_names.items():
                verbose = group._meta.get_field(field).verbose_name
                self.assertEqual(verbose, verbose_name)

    def test_object_name_is_title_field(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
