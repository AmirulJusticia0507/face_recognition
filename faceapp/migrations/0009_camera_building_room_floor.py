from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faceapp', '0008_fix_violationlog_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('source', models.CharField(choices=[
                    ('jogjakota', 'Jogja Kota (cctv.jogjakota.go.id)'),
                    ('sleman', 'Sleman (24jam.slemankab.go.id)'),
                    ('bantul', 'Bantul (bantulkab.go.id)'),
                    ('ai_cctv', 'AI CCTV External'),
                    ('custom', 'Stream URL Custom'),
                ], max_length=20)),
                ('stream_url', models.URLField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(choices=[
                    ('online', 'Online'),
                    ('offline', 'Offline'),
                    ('maintenance', 'Maintenance'),
                ], default='online', max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('building', models.CharField(blank=True, max_length=100, null=True, verbose_name='Gedung/Lokasi')),
                ('room', models.CharField(blank=True, max_length=100, null=True, verbose_name='Ruangan')),
                ('floor', models.CharField(blank=True, max_length=20, null=True, verbose_name='Lantai')),
                ('auto_scan', models.BooleanField(default=False, verbose_name='Scan Otomatis Aktif')),
                ('scan_interval_seconds', models.PositiveIntegerField(default=30, verbose_name='Interval Scan (detik)')),
                ('last_scanned_at', models.DateTimeField(blank=True, null=True, verbose_name='Scan Terakhir')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
