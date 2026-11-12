from django.core.exceptions import ValidationError

from nautobot.core.testing import TestCase
from nautobot.extras.models import Status
from nautobot.ipam.forms import IPAddressBulkEditForm
from nautobot.ipam.models import IPAddress, Namespace, Prefix
from nautobot.ipam.validators import DNSValidator


class DNSValidatorTest(TestCase):
    VALID = [
        "",
        "router1",
        "Host.Example.COM",
        "xn--bcher-kva.example",
        "example.com.",
        "a" * 63 + ".example",
        ".".join(["a" * 61] * 4) + ".",  # 4*61 + 3 dots = 247
        ".".join(["a" * 63, "b" * 63, "c" * 63, "d" * 61]),  # exactly 253
    ]
    INVALID = [
        "whatever-.your.tld",
        "-a.example",
        "a..b",
        ".a",
        "a..",
        ".",
        "host_name.example",
        "_sip.example",
        "a" * 64 + ".example",
        ".".join(["a" * 63, "b" * 63, "c" * 63, "d" * 62]),  # 254
        "bücher.example",
        "has space.example",
    ]

    def test_valid(self):
        for name in self.VALID:
            with self.subTest(name=name):
                DNSValidator(name)

    def test_invalid(self):
        for name in self.INVALID:
            with self.subTest(name=name):
                with self.assertRaises(ValidationError):
                    DNSValidator(name)

    def test_model_validated_save(self):
        status = Status.objects.get_for_model(IPAddress).first()
        namespace = Namespace.objects.first() or Namespace.objects.create(name="dns-test")
        Prefix.objects.get_or_create(
            prefix="10.99.0.0/24",
            namespace=namespace,
            defaults={"status": Status.objects.get_for_model(Prefix).first()},
        )
        ip = IPAddress(address="10.99.0.1/24", status=status, namespace=namespace, dns_name="whatever-.your.tld")
        with self.assertRaises(ValidationError) as cm:
            ip.validated_save()
        self.assertIn("dns_name", cm.exception.message_dict)

        ip.dns_name = "Host.Example.COM."
        ip.validated_save()
        ip.refresh_from_db()
        self.assertEqual(ip.dns_name, "host.example.com.")

    def test_bulk_edit_form(self):
        form = IPAddressBulkEditForm(model=IPAddress, data={"pk": [], "dns_name": "a..b"})
        self.assertFalse(form.is_valid())
        self.assertIn("dns_name", form.errors)
