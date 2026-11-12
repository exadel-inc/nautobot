from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator


def prefix_validator(prefix):
    if prefix.ip != prefix.cidr.ip:
        raise ValidationError(f"{prefix} is not a valid prefix. Did you mean {prefix.cidr}?")


class MaxPrefixLengthValidator(BaseValidator):
    message = "The prefix length must be less than or equal to %(limit_value)s."
    code = "max_prefix_length"

    def compare(self, a, b):
        return a.prefixlen > b


class MinPrefixLengthValidator(BaseValidator):
    message = "The prefix length must be greater than or equal to %(limit_value)s."
    code = "min_prefix_length"

    def compare(self, a, b):
        return a.prefixlen < b


# RFC 952/1123 hostname: dot-separated labels of 1-63 ASCII letters, digits or hyphens (not starting or ending
# with a hyphen), at most 253 characters excluding one optional trailing dot. Underscores are not allowed.
DNSValidator = RegexValidator(
    regex=r"^(?=.{1,253}\.?\Z)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?\Z",
    message=(
        "Enter a valid DNS name: labels of 1-63 letters, digits or hyphens, not starting or ending with a hyphen, "
        "separated by single periods (253 characters max)."
    ),
    code="invalid",
)
