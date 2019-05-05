# Generated by Django 2.1.7 on 2019-03-07 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayingGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('player1', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('player2', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('player3', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('player4', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('player5', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('player6', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('player7', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('player8', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('player9', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('player10', models.CharField(blank=True, choices=[('ch', 'ch'), ('cx', 'cx'), ('fwk', 'fwk'), ('hcd', 'hcd'), ('hlk', 'hlk'), ('lhy', 'lhy'), ('lq', 'lq'), ('lsk', 'lsk'), ('lwq', 'lwq'), ('mzh', 'mzh'), ('pc', 'pc'), ('qfy', 'qfy'), ('yzh', 'yzh')], max_length=16, null=True)),
                ('hero1', models.CharField(blank=True, max_length=32, null=True)),
                ('hero2', models.CharField(blank=True, max_length=32, null=True)),
                ('hero3', models.CharField(blank=True, max_length=32, null=True)),
                ('hero4', models.CharField(blank=True, max_length=32, null=True)),
                ('hero5', models.CharField(blank=True, max_length=32, null=True)),
                ('hero6', models.CharField(blank=True, max_length=32, null=True)),
                ('hero7', models.CharField(blank=True, max_length=32, null=True)),
                ('hero8', models.CharField(blank=True, max_length=32, null=True)),
                ('hero9', models.CharField(blank=True, max_length=32, null=True)),
                ('hero10', models.CharField(blank=True, max_length=32, null=True)),
            ],
        ),
    ]
