# Migration: fix ViolationLog fields
# - plate_number: allow blank, default UNKNOWN
# - vehicle_image: allow null/blank (auto-detected violations have no image)
# - add camera_name field
# - add description field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faceapp', '0007_modelsetting_person_address_person_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='violationlog',
            name='plate_number',
            field=models.CharField(blank=True, default='UNKNOWN', max_length=20),
        ),
        migrations.AlterField(
            model_name='violationlog',
            name='vehicle_image',
            field=models.ImageField(blank=True, null=True, upload_to='violations/'),
        ),
        migrations.AddField(
            model_name='violationlog',
            name='camera_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='violationlog',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
