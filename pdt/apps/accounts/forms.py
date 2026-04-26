from django import forms

from .models import User


class ProfileSetupForm(forms.ModelForm):
    """Formulário usado logo após o cadastro para coletar os dados de carreira."""

    class Meta:
        model = User
        fields = [
            "full_name",
            "country",
            "bio",
            "linkedin_url",
            "github_url",
            "show_in_leaderboard",
            "show_contact_info",
            "show_on_map",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        data = super().clean()
        if not data.get("linkedin_url") and not data.get("github_url"):
            raise forms.ValidationError(
                "Informe ao menos um perfil profissional (LinkedIn ou GitHub). "
                "Esses dados ajudam quem se destaca a ser visto pelo mercado."
            )
        return data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "full_name",
            "country",
            "bio",
            "linkedin_url",
            "github_url",
            "show_in_leaderboard",
            "show_contact_info",
            "show_on_map",
        ]
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}
