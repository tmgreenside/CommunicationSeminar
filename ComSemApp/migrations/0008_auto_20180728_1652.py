# Generated by Django 2.0 on 2018-07-28 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ComSemApp', '0007_worksheet_topic_char_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='worksheet',
            name='topic',
        ),
        migrations.DeleteModel(
            name='Topic',
        ),
    ]