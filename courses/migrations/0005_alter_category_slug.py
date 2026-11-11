from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=200
            ),
        ),
    ]