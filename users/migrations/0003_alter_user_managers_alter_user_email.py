
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_member"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[],
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=255, unique=True),
        ),
    ]
