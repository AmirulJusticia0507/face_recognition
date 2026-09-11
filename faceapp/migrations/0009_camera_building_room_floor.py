from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faceapp', '0008_fix_violationlog_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='building',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Gedung/Lokasi'),
        ),
        migrations.AddField(
            model_name='camera',
            name='room',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ruangan'),
        ),
        migrations.AddField(
            model_name='camera',
            name='floor',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Lantai'),
        ),
    ]
