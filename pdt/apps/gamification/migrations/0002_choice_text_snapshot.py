from django.db import migrations, models


def backfill_choice_text(apps, schema_editor):
    """Preenche o snapshot para respostas já gravadas, a partir do texto
    ATUAL da Choice referenciada. Não é perfeito — se a Choice já tiver sido
    reescrita pelo seed desde a resposta, o snapshot carrega o texto novo, não
    o que o usuário viu — mas é estritamente melhor que "(em branco)" para
    quem nem chegou a responder."""
    TopicAttemptAnswer = apps.get_model("gamification", "TopicAttemptAnswer")
    for answer in TopicAttemptAnswer.objects.filter(
        choice__isnull=False, choice_text=""
    ).select_related("choice"):
        answer.choice_text = answer.choice.text
        answer.save(update_fields=["choice_text"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("gamification", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="topicattemptanswer",
            name="choice_text",
            field=models.CharField(
                blank=True,
                default="",
                max_length=255,
                help_text=(
                    "Snapshot do texto da alternativa marcada, gravado no momento "
                    "da resposta. `choice` é FK para `courses.Choice` e vira NULL "
                    "quando o seed apaga e recria as alternativas — sem este "
                    "snapshot, o histórico de tentativas antigas passava a mostrar "
                    "'(em branco)' para respostas que o usuário de fato tinha dado."
                ),
            ),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_choice_text, noop_reverse),
    ]
