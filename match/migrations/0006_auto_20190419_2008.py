# Generated by Django 2.1.7 on 2019-04-19 12:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0005_appearance_herostats_playerinterstats_playerstats'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appearance',
            name='id',
        ),
        migrations.RemoveField(
            model_name='herostats',
            name='id',
        ),
        migrations.RemoveField(
            model_name='playerinterstats',
            name='id',
        ),
        migrations.RemoveField(
            model_name='playerstats',
            name='id',
        ),
        migrations.AddField(
            model_name='appearance',
            name='name',
            field=models.CharField(default=1, max_length=16, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='herostats',
            name='name',
            field=models.CharField(default=django.utils.timezone.now, max_length=16, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playerinterstats',
            name='name',
            field=models.CharField(default=1, max_length=16, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playerstats',
            name='name',
            field=models.CharField(default=1, max_length=16, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
