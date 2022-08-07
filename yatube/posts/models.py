from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


# Create your models here.
class Group(models.Model):
    title = models.CharField(
        max_length=200
    )
    slug = models.SlugField(
        unique=True
    )
    description = models.TextField(
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Содержание записи',
        help_text='Напишите что-нибудь интересное',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Название группы',
        help_text='Введите название группы',
    )

    def __str__(self):
        return f'{self.author.username}, {self.group} - {self.text[:15]}'
