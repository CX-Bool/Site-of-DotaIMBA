# Generated by Django 2.1.7 on 2019-03-10 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0003_auto_20190310_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='sigma',
            field=models.FloatField(default=8.333),
        ),
    ]