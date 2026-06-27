from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0005_add_spark_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='resume',
            field=models.FileField(upload_to='resumes/', null=True, blank=True),
        ),
    ]
