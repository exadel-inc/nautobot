import re

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator


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


_DNS_LABEL_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")
_DNS_MAX_LENGTH = 253


def DNSValidator(value):  # pylint: disable=invalid-name
    """Validate an RFC 952/1123 hostname or FQDN (ASCII only, optional single trailing root dot); blank is allowed."""
    if not value:
        return
    name = value[:-1] if value.endswith(".") else value
    if len(name) > _DNS_MAX_LENGTH or not all(_DNS_LABEL_RE.fullmatch(label) for label in name.split(".")):
        raise ValidationError(
            "Enter a valid DNS name: labels of 1-63 letters, digits or hyphens, not starting or ending with a "
            "hyphen, separated by single periods, at most 253 characters in total.",
            code="invalid",
        )
