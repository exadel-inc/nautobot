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


_DNS_LABEL = r"[0-9A-Za-z_](?:[0-9A-Za-z_-]{0,61}[0-9A-Za-z_])?"

DNSValidator = RegexValidator(
    # The lookahead caps the total length at 253 characters, not counting one optional trailing dot.
    regex=rf"^(?=.{{1,253}}\.?$){_DNS_LABEL}(?:\.{_DNS_LABEL})*\.?$",
    message=(
        "DNS names must consist of dot-separated labels of 1-63 alphanumeric, hyphen or underscore characters, "
        "not beginning or ending with a hyphen, with a maximum total length of 253 characters."
    ),
    code="invalid",
)
