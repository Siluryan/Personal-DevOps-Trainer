class SeedLockingAdminMixin:
    """Marca `seed_managed=False` ao editar qualquer campo pelo admin.

    A partir daí, o management command de seed correspondente para de
    sobrescrever este registro — é o que torna editar algo pelo admin (uma
    aula, uma questão, um termo de glossário) uma mudança que sobrevive ao
    próximo deploy, em vez de ser revertida no dia seguinte.

    Se o próprio `seed_managed` foi mexido no formulário, respeita a escolha
    explícita do mantenedor (ex.: religar o campo para voltar a sincronizar
    com o seed) em vez de forçá-lo de volta a False — senão o checkbox
    apareceria no form mas nunca "colaria" o valor marcado.
    """

    def save_model(self, request, obj, form, change):
        if "seed_managed" not in form.changed_data and form.changed_data:
            obj.seed_managed = False
        super().save_model(request, obj, form, change)
