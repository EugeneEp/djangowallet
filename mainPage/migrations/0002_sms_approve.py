# Generated by Django 3.1.2 on 2020-10-30 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainPage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sms_approve',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('code', models.IntegerField()),
                ('action', models.CharField(blank=True, max_length=255, null=True)),
                ('time', models.IntegerField(default=1604070563.6459773)),
                ('status', models.IntegerField(default=0)),
                ('phone', models.CharField(max_length=255)),
            ],
        ),
    ]
