# Generated migration to rename duration field to distance

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0002_alter_airport_position'),
    ]

    operations = [
        # Rename the field from duration to distance
        migrations.RenameField(
            model_name='route',
            old_name='duration',
            new_name='distance',
        ),
        # Update the field help text
        migrations.AlterField(
            model_name='route',
            name='distance',
            field=models.IntegerField(help_text='Flight distance in kilometers'),
        ),
    ]
