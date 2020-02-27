import coreapi

from rest_framework.filters import BaseFilterBackend


class MonthlyReportFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name="start_date", location="query", required=False, type="string"
            )
        ]
