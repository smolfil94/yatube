# Generated by Django 2.2.6 on 2020-12-13 19:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created'], 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
    ]
