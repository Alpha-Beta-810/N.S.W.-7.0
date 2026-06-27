# Migration for all SPARK fields added to models.py
# that are missing from the database (0001-0004 never created them).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0004_application_resume'),
    ]

    operations = [
        # ── Personal ─────────────────────────────────────────────────
        migrations.AddField(
            model_name='application', name='title',
            field=models.CharField(max_length=5, default='Mr'),
        ),
        migrations.AddField(
            model_name='application', name='nationality',
            field=models.CharField(max_length=100, default='Indian'),
        ),
        migrations.AddField(
            model_name='application', name='mobile',
            field=models.CharField(max_length=20, default=''),
            preserve_default=False,
        ),

        # ── Current Academic ──────────────────────────────────────────
        migrations.AddField(
            model_name='application', name='course_other',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='application', name='institute_category',
            field=models.CharField(max_length=50, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='application', name='course_duration',
            field=models.CharField(max_length=20),
        ),

        # ── Previous Academic ─────────────────────────────────────────
        migrations.AddField(
            model_name='application', name='prev_institute_category',
            field=models.CharField(max_length=50, blank=True, default=''),
            preserve_default=False,
        ),

        # ── Project / Internship ──────────────────────────────────────
        migrations.AddField(
            model_name='application', name='scheme',
            field=models.CharField(max_length=30, default='Internship'),
        ),
        migrations.AddField(
            model_name='application', name='internship_from',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='application', name='internship_to',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='application', name='duration_months',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='application', name='area_of_interest',
            field=models.CharField(max_length=200, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='application', name='area_other',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),

        # ── University Guide ──────────────────────────────────────────
        migrations.AddField(
            model_name='application', name='guide_name',
            field=models.CharField(max_length=200, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='application', name='guide_designation',
            field=models.CharField(max_length=200, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='application', name='guide_department',
            field=models.CharField(max_length=200, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='application', name='guide_email',
            field=models.EmailField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='application', name='guide_phone',
            field=models.CharField(max_length=20, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='application', name='csir_guide_name',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),

        # ── Other ─────────────────────────────────────────────────────
        migrations.AddField(
            model_name='application', name='other_info',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='application', name='project_interest',
            field=models.TextField(blank=True),
        ),
    ]
