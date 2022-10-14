# from collections import defaultdict

# import i18naddress
# from django import forms
# from django.core.exceptions import ValidationError
# from django.forms.forms import BoundField  # type: ignore
# from django_countries import countries

# from .models import Address
# from .validators import validate_possible_number
# from .widgets import DatalistTextWidget

# COUNTRY_FORMS = {}
# UNKNOWN_COUNTRIES = set()

# AREA_TYPE = {
#     "area": "Area",
#     "county": "County",
#     "department": "Department",
#     "district": "District",
#     "do_si": "Do/si",
#     "eircode": "Eircode",
#     "emirate": "Emirate",
#     "island": "Island",
#     "neighborhood": "Neighborhood",
#     "oblast": "Oblast",
#     "parish": "Parish",
#     "pin": "PIN",
#     "postal": "Postal code",
#     "prefecture": "Prefecture",
#     "province": "Province",
#     "state": "State",
#     "suburb": "Suburb",
#     "townland": "Townland",
#     "village_township": "Village/township",
#     "zip": "ZIP code",
# }


# class PossiblePhoneNumberFormField(forms.CharField):
#     """A phone input field."""

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.widget.input_type = "tel"



# def update_base_fields(form_class, i18n_rules):
#     for field_name, label_value in AddressForm.Meta.labels.items():
#         field = form_class.base_fields[field_name]
#         field.label = label_value

#     for field_name, placeholder_value in AddressForm.Meta.placeholders.items():
#         field = form_class.base_fields[field_name]
#         field.placeholder = placeholder_value

#     if i18n_rules.country_area_choices:
#         required = "country_area" in i18n_rules.required_fields
#         form_class.base_fields["country_area"] = CountryAreaChoiceField(
#             choices=i18n_rules.country_area_choices, required=required
#         )

#     labels_map = {
#         "country_area": i18n_rules.country_area_type,
#         "postal_code": i18n_rules.postal_code_type,
#         "city_area": i18n_rules.city_area_type,
#     }

#     for field_name, area_type in labels_map.items():
#         field = form_class.base_fields[field_name]
#         field.label = AREA_TYPE[area_type]

#     hidden_fields = i18naddress.KNOWN_FIELDS - i18n_rules.allowed_fields
#     for field_name in hidden_fields:
#         if field_name in form_class.base_fields:
#             form_class.base_fields[field_name].widget = forms.HiddenInput()

#     country_field = form_class.base_fields["country"]
#     country_field.choices = COUNTRY_CHOICES


# def construct_address_form(country_code, i18n_rules):
#     class_name = "AddressForm%s" % country_code
#     base_class = CountryAwareAddressForm
#     form_kwargs = {
#         "Meta": type(str("Meta"), (base_class.Meta, object), {}),
#         "formfield_callback": None,
#     }
#     class_ = type(base_class)(str(class_name), (base_class,), form_kwargs)
#     update_base_fields(class_, i18n_rules)
#     class_.i18n_country_code = country_code
#     class_.i18n_fields_order = property(get_form_i18n_lines)
#     return class_


# for country in countries.countries.keys():
#     try:
#         country_rules = i18naddress.get_validation_rules({"country_code": country})
#     except ValueError:
#         country_rules = i18naddress.get_validation_rules({})
#         UNKNOWN_COUNTRIES.add(country)

# COUNTRY_CHOICES = [
#     (code, label)
#     for code, label in countries.countries.items()
#     if code not in UNKNOWN_COUNTRIES
# ]
# # Sort choices list by country name
# COUNTRY_CHOICES = sorted(COUNTRY_CHOICES, key=lambda choice: choice[1])

# for country, label in COUNTRY_CHOICES:
#     country_rules = i18naddress.get_validation_rules({"country_code": country})
#     COUNTRY_FORMS[country] = construct_address_form(country, country_rules)
