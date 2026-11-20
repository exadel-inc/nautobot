from django.core.management.base import BaseCommand
from graphene_django.settings import graphene_settings
from graphql import GraphQLError, parse, validate

from nautobot.core.graphql import execute_query
from nautobot.users.models import User


class Command(BaseCommand):
    help = "Audit all existing GraphQLQuery instances in the database and output invalid query data"

    def handle(self, *args, **options):
        from nautobot.extras.models import GraphQLQuery

        self.stdout.write("\n>>> Auditing existing GraphQLQuery data for invalid queries ...\n")

        graph_ql_querys = GraphQLQuery.objects.all().order_by("name")
        user, _ = User.objects.get_or_create(username="GraphQL Test User")
        is_valid = True
        error_dict = {}
        for graph_ql_query in graph_ql_querys:
            try:
                # execute() alone doesn't validate the query against the schema (e.g. unknown fields), so do it here
                errors = validate(graphene_settings.SCHEMA.graphql_schema, parse(graph_ql_query.query))
                if not errors:
                    errors = execute_query(graph_ql_query.query, user=user).errors
            except GraphQLError as err:
                # Syntactically invalid queries raise while parsing rather than being returned as result errors
                errors = [err]
            if errors:
                error_dict[graph_ql_query.name] = [error.formatted for error in errors]
                is_valid = False
        if is_valid:
            self.stdout.write("\n>>> All GraphQLQuery query data are validated successfully!")
        else:
            self.stderr.write(">>> The following GraphQLQuery instances have invalid query data: \n")
            for name, error_message in error_dict.items():
                self.stderr.write(
                    f"    GraphQLQuery instance with name `{name}` has invalid query data: {error_message}\n"
                )

            self.stderr.write(
                "\n>>> Please fix the outdated query data stated above according to the documentation available at:\n"
                "https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/upgrading/from-v1/upgrading-from-nautobot-v1/#ui-graphql-and-rest-api-filter-changes\n"
            )
