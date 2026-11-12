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


DNSValidator = RegexValidator(
    # One or more dot-separated labels, each 1-63 chars of letters/digits/hyphens, not starting or
    # ending with a hyphen, followed by an optional single trailing root dot. The leading lookahead
    # enforces the 253-char limit on the name excluding that optional trailing dot (RFC 952/1123).
    regex=r"^(?=.{1,253}\.?\Z)[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*\.?\Z",
    message=(
        "This field may only contain letters, digits, and hyphens, with periods separating individual "
        "labels. Each label must be 1-63 characters, cannot begin or end with a hyphen, and the entire "
        "name may not exceed 253 characters (excluding an optional trailing period)."
    ),
    code="invalid",
)
