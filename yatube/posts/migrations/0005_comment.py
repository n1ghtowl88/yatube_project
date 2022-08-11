# Generated by Django 2.2.19 on 2022-08-10 15:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0004_auto_20220809_1232'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Прокомментируйте запись', verbose_name='Содержание комментария')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата комментирования')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('post', models.ForeignKey(help_text='Напишите комментарий к посту', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='Коментарий')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
    ]