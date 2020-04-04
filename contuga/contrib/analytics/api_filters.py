import coreapi

from rest_framework.filters import BaseFilterBackend


class ReportsFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name="report_unit", location="query", required=False, type="string"
            ),
            coreapi.Field(
                name="start_date", location="query", required=False, type="string"
            ),
        ]
