from django.contrib.auth import get_user_model

from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Ключ',
        max_length=100,
        null=False,
        unique=True)

    class Meta:
        verbose_name = 'Сообщества'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст',
        help_text='Введите текст записи')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name="posts")
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True, null=True,
        help_text='При необходимости укажите сообщество')
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикация'

    def __str__(self):
        text = self.text[:15]
        return f'{text}... Автор: {self.author}. Дата: {self.pub_date}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        text = self.text[:25]
        post = self.post
        return (f'{text}... Автор: {self.author}. Дата: {self.created}'
                f'(Пост: {post.id}. {post.text[:15]}, ' 
                f'Автор: {post.author.username})')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )
