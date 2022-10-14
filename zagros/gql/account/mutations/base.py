import graphene
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from graphql_jwt.exceptions import PermissionDenied

from ....account import CustomerEvents as account_events, models
from ....account.emails import (
    send_set_password_email_with_url,
    send_user_password_reset_email_with_url,
)
from ....account.error_codes import AccountErrorCode
from ....core.permissions import AccountPermissions
from ....core.utils.url import validate_storefront_url
# from ....order.utils import match_orders_with_new_user

from ...account.types import User
from ...core.mutations import (
    BaseMutation,
    ModelDeleteMutation,
    ModelMutation,
    validation_error_to_error_type,
)
from .jwt import CreateToken
from ...core.types.common import AccountError
from ...meta.deprecated.mutations import ClearMetaBaseMutation, UpdateMetaBaseMutation

INVALID_TOKEN = "Invalid or expired token."



class SetPassword(CreateToken):
    class Arguments:
        token = graphene.String(
            description="A one-time token required to set the password.", required=True
        )
        email = graphene.String(required=True, description="Email of a user.")
        password = graphene.String(required=True, description="Password of a user.")

    class Meta:
        description = (
            "Sets the user's password from the token sent by email "
            "using the RequestPasswordReset mutation."
        )
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def mutate(cls, root, info, **data):
        email = data["email"]
        password = data["password"]
        token = data["token"]

        try:
            cls._set_password_for_user(email, password, token)
        except ValidationError as e:
            errors = validation_error_to_error_type(e)
            return cls.handle_typed_errors(errors)
        return super().mutate(root, info, **data)


class RequestPasswordReset(BaseMutation):
    class Arguments:
        email = graphene.String(
            required=True,
            description="Email of the user that will be used for password recovery.",
        )
        redirect_url = graphene.String(
            required=True,
            description=(
                "URL of a view where users should be redirected to "
                "reset the password. URL in RFC 1808 format."
            ),
        )

    class Meta:
        description = "Sends an email with the account password modification link."
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        email = data["email"]
        redirect_url = data["redirect_url"]
        try:
            validate_storefront_url(redirect_url)
        except ValidationError as error:
            raise ValidationError(
                {"redirect_url": error}, code=AccountErrorCode.INVALID
            )

        try:
            user = models.User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise ValidationError(
                {
                    "email": ValidationError(
                        "User with this email doesn't exist",
                        code=AccountErrorCode.NOT_FOUND,
                    )
                }
            )
        send_user_password_reset_email_with_url(redirect_url, user)
        return RequestPasswordReset()


class ConfirmAccount(BaseMutation):
    user = graphene.Field(User, description="An activated user account.")

    class Arguments:
        token = graphene.String(
            description="A one-time token required to confirm the account.",
            required=True,
        )
        email = graphene.String(
            description="E-mail of the user performing account confirmation.",
            required=True,
        )

    class Meta:
        description = (
            "Confirm user account with token sent by email during registration."
        )
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        try:
            user = models.User.objects.get(email=data["email"])
        except ObjectDoesNotExist:
            raise ValidationError(
                {
                    "email": ValidationError(
                        "User with this email doesn't exist",
                        code=AccountErrorCode.NOT_FOUND,
                    )
                }
            )

        if not default_token_generator.check_token(user, data["token"]):
            raise ValidationError(
                {"token": ValidationError(INVALID_TOKEN, code=AccountErrorCode.INVALID)}
            )

        user.is_active = True
        user.save(update_fields=["is_active"])
        # match_orders_with_new_user(user)
        return ConfirmAccount(user=user)


class PasswordChange(BaseMutation):
    user = graphene.Field(User, description="A user instance with a new password.")

    class Arguments:
        old_password = graphene.String(
            required=True, description="Current user password."
        )
        new_password = graphene.String(required=True, description="New user password.")

    class Meta:
        description = "Change the password of the logged in user."
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        user = info.context.user
        old_password = data["old_password"]
        new_password = data["new_password"]

        if not user.check_password(old_password):
            raise ValidationError(
                {
                    "old_password": ValidationError(
                        "Old password isn't valid.",
                        code=AccountErrorCode.INVALID_CREDENTIALS,
                    )
                }
            )
        try:
            password_validation.validate_password(new_password, user)
        except ValidationError as error:
            raise ValidationError({"new_password": error})

        user.set_password(new_password)
        user.save(update_fields=["password"])
        account_events.customer_password_changed_event(user=user)
        return PasswordChange(user=user)




class UserInput(graphene.InputObjectType):
    first_name = graphene.String(description="Given name.")
    last_name = graphene.String(description="Family name.")
    email = graphene.String(description="The unique email address of the user.")
    is_active = graphene.Boolean(required=False, description="User account is active.")
    note = graphene.String(description="A note about the user.")




class CustomerInput(UserInput):
    pass


class UserCreateInput(CustomerInput):
    redirect_url = graphene.String(
        description=(
            "URL of a view where users should be redirected to "
            "set the password. URL in RFC 1808 format."
        )
    )


class BaseCustomerCreate(ModelMutation):
    """Base mutation for customer create used by staff and account."""

    class Arguments:
        input = UserCreateInput(
            description="Fields required to create a customer.", required=True
        )

    class Meta:
        abstract = True

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)

        if cleaned_input.get("redirect_url"):
            try:
                validate_storefront_url(cleaned_input.get("redirect_url"))
            except ValidationError as error:
                raise ValidationError(
                    {"redirect_url": error}, code=AccountErrorCode.INVALID
                )

        return cleaned_input

    @classmethod
    @transaction.atomic
    def save(cls, info, instance, cleaned_input):

        is_creation = instance.pk is None
        super().save(info, instance, cleaned_input)

        # The instance is a new object in db, create an event
        if is_creation:
            info.context.plugins.customer_created(customer=instance)
            account_events.customer_account_created_event(user=instance)

        if cleaned_input.get("redirect_url"):
            send_set_password_email_with_url(
                cleaned_input.get("redirect_url"), instance
            )


class UserUpdateMeta(UpdateMetaBaseMutation):
    class Meta:
        description = "Updates metadata for user."
        model = models.User
        public = True
        error_type_class = AccountError
        error_type_field = "account_errors"
        permissions = (AccountPermissions.MANAGE_USERS,)


class UserClearMeta(ClearMetaBaseMutation):
    class Meta:
        description = "Clear metadata for user."
        model = models.User
        public = True
        error_type_class = AccountError
        error_type_field = "account_errors"
        permissions = (AccountPermissions.MANAGE_USERS,)
