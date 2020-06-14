# Generated by Django 3.0.7 on 2020-06-14 06:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20200613_2229'),
    ]

    operations = [
        migrations.CreateModel(
            name='Youtube',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('youtube_link', models.URLField()),
                ('youtube_title', models.CharField(max_length=150)),
            ],
        ),
        migrations.RemoveField(
            model_name='card',
            name='youtube_link',
        ),
        migrations.RemoveField(
            model_name='card',
            name='youtube_title',
        ),
        migrations.AddField(
            model_name='card',
            name='youtube',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Youtube'),
        ),
    ]
