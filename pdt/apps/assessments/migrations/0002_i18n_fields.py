from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="admissionquestion",
            name="statement_en",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="admissionquestion",
            name="explanation_en",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="admissionchoice",
            name="text_en",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
    ]
