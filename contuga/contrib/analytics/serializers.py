from rest_framework import serializers


class CurrencySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=254)
    code = serializers.CharField(max_length=3)


class ReportItemSerializer(serializers.Serializer):
    day = serializers.IntegerField(required=False)
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    income = serializers.DecimalField(max_digits=14, decimal_places=2)
    expenditures = serializers.DecimalField(max_digits=14, decimal_places=2)
    balance = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)


class ReportsSerializer(serializers.Serializer):
    report_unit = serializers.CharField(write_only=True)
    start_date = serializers.DateField(write_only=True)
    pk = serializers.UUIDField()
    name = serializers.CharField()
    currency = CurrencySerializer()
    reports = ReportItemSerializer(many=True)
