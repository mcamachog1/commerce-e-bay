# Generated by Django 4.0.3 on 2022-07-23 20:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_auctionlist_url_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionlist',
            name='date_creation',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='auctionlist',
            name='date_update',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='auctionlist',
            name='url_image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
