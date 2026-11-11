from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_advertisement'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=200,
                null=True
            ),
        ),
    ]