# Generated by Django 4.2.7 on 2023-12-16 04:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('brews', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrewSwap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.TextField(choices=[('Live', 'Live'), ('Complete', 'Complete'), ('Inactive', 'Inactive')], default='Inactive')),
                ('total_bottles', models.IntegerField()),
                ('max_increment', models.IntegerField(default=6)),
                ('brew', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='swap', to='brews.brew')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_creator', to=settings.AUTH_USER_MODEL)),
                ('updater', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updater', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SwapClaim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('num_bottles', models.IntegerField()),
                ('status', models.TextField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending')),
                ('brew', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='brews.brew')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_creator', to=settings.AUTH_USER_MODEL)),
                ('swap', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='claims', to='brewswaps.brewswap')),
                ('updater', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updater', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
