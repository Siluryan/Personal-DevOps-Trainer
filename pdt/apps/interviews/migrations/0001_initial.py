from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0003_user_career_level"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InterviewQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("junior", "Júnior"),
                            ("pleno", "Pleno"),
                            ("senior", "Sênior"),
                        ],
                        max_length=12,
                    ),
                ),
                ("category", models.CharField(blank=True, max_length=80)),
                ("statement", models.TextField()),
                (
                    "choices",
                    models.JSONField(
                        default=list,
                        help_text="Lista de strings com as alternativas, em ordem.",
                    ),
                ),
                ("correct_index", models.PositiveSmallIntegerField()),
                ("explanation", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["level", "order", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="interviewquestion",
            index=models.Index(
                fields=["level", "is_active"], name="interviews__level_e9ec33_idx"
            ),
        ),
        migrations.CreateModel(
            name="InterviewAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("junior", "Júnior"),
                            ("pleno", "Pleno"),
                            ("senior", "Sênior"),
                        ],
                        max_length=12,
                    ),
                ),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("question_ids", models.JSONField(default=list)),
                ("answers", models.JSONField(default=dict)),
                ("score", models.PositiveSmallIntegerField(default=0)),
                ("passed", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="interview_attempts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-started_at"],
            },
        ),
        migrations.AddIndex(
            model_name="interviewattempt",
            index=models.Index(
                fields=["user", "level", "finished_at"],
                name="interviews__user_id_5e8aaa_idx",
            ),
        ),
    ]
