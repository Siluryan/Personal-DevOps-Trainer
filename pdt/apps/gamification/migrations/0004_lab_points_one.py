from django.db import migrations


def recompute_lab_bonus(apps, schema_editor):
    TopicScore = apps.get_model("gamification", "TopicScore")
    LabCompletion = apps.get_model("gamification", "LabCompletion")
    for score in TopicScore.objects.all().iterator():
        done = LabCompletion.objects.filter(
            user_id=score.user_id,
            lab__topic_id=score.topic_id,
            lab__is_active=True,
        ).count()
        score.lab_bonus = done  # LAB_POINTS = 1
        score.points = score.best_quiz_score + score.help_bonus + score.lab_bonus
        score.save(update_fields=["lab_bonus", "points"])


def noop(apps, schema_editor):
    return None


class Migration(migrations.Migration):

    dependencies = [
        ("gamification", "0003_lab_completion"),
        ("courses", "0005_lab_lesson_page"),
    ]

    operations = [
        migrations.RunPython(recompute_lab_bonus, noop),
    ]
