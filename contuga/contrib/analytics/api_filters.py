from rest_framework.filters import BaseFilterBackend


class ReportsFilterBackend(BaseFilterBackend):
    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "report_unit",
                "required": False,
                "in": "query",
                "description": "",
                "schema": {
                    "type": "string",
                },
            },
            {
                "name": "start_date",
                "required": False,
                "in": "query",
                "description": "",
                "schema": {
                    "type": "string",
                },
            },
        ]
