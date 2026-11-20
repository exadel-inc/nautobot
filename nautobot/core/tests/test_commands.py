from io import StringIO

from django.core.management import call_command
import yaml

from nautobot.core.testing import TestCase
from nautobot.extras.models import GraphQLQuery


class ManagementCommandTestCase(TestCase):
    """Test case for core management commands."""

    def setUp(self):
        """Initialize user and client."""
        super().setUpNautobot()
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)

    def test_generate_performance_test_endpoints(self):
        """Test the generate_performance_test_endpoints management command."""
        out = StringIO()
        call_command("generate_performance_test_endpoints", stdout=out)
        endpoints_dict = yaml.safe_load(out.getvalue())["endpoints"]
        for view_name, value in endpoints_dict.items():
            for endpoint in value:
                with self.subTest(endpoint=endpoint):
                    response = self.client.get(endpoint, follow=True)
                    self.assertHttpStatus(
                        response,
                        200,
                        f"{view_name}: {endpoint} returns status Code {response.status_code} instead of 200",
                    )

    def test_audit_graphql_queries_all_valid(self):
        GraphQLQuery.objects.create(name="Valid query", query="query { devices { name } }")
        out, err = StringIO(), StringIO()
        call_command("audit_graphql_queries", stdout=out, stderr=err)
        self.assertIn("All GraphQLQuery query data are validated successfully!", out.getvalue())
        self.assertEqual(err.getvalue(), "")

    def test_audit_graphql_queries_reports_only_invalid_query(self):
        GraphQLQuery.objects.create(name="Valid control", query="query { devices { name } }")
        GraphQLQuery.objects.create(name="Outdated query", query="query { devices { nonexistent_field } }")
        out, err = StringIO(), StringIO()
        call_command("audit_graphql_queries", stdout=out, stderr=err)
        self.assertNotIn("validated successfully", out.getvalue())
        self.assertIn("Outdated query", err.getvalue())
        self.assertIn("nonexistent_field", err.getvalue())
        self.assertNotIn("Valid control", err.getvalue())
