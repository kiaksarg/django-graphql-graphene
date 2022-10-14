
import graphene
from django.conf import settings
from django.utils import translation
from django_countries import countries

from ...core.permissions import get_permissions
from ..decorators import permission_required
from ..utils import format_permissions_for_display
from ..core.types.common import CountryDisplay,LanguageDisplay, Permission
from ..translations.enums import LanguageCodeEnum
from ..core.utils import str_to_enum



class Site(graphene.ObjectType):

    permissions = graphene.List(
        Permission, description="List of available permissions.", required=True
    )

    class Meta:
        description = (
            "Represents site resource containing general site data and configuration."
        )

    countries = graphene.List(
        graphene.NonNull(CountryDisplay),
        language_code=graphene.Argument(
            LanguageCodeEnum,
            description="A language code to return the translation for.",
        ),
        description="List of countries available in the site.",
    )

    languages = graphene.List(
        LanguageDisplay,
        description="List of the shops's supported languages.",
    )


    @staticmethod
    def resolve_permissions(_, _info):
        permissions = get_permissions()
        return format_permissions_for_display(permissions)

    @staticmethod
    def resolve_countries(_, _info, language_code=None):
        with translation.override(language_code):
            return [
                CountryDisplay(
                    code=country[0], country=country[1]
                )
                for country in countries
            ]

    @staticmethod
    def resolve_languages(_, _info):
        return [
            LanguageDisplay(
                code=LanguageCodeEnum[str_to_enum(language[0])], language=language[1]
            )
            for language in settings.LANGUAGES
        ]
