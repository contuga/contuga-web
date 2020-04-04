from rest_framework import serializers

from contuga.contrib.accounts import constants


class ReportItemSerializer(serializers.Serializer):
    day = serializers.IntegerField(required=False)
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    income = serializers.DecimalField(max_digits=14, decimal_places=2)
    expenditures = serializers.DecimalField(max_digits=14, decimal_places=2)
    balance = serializers.DecimalField(max_digits=14, decimal_places=2)


class ReportsSerializer(serializers.Serializer):
    report_unit = serializers.CharField(write_only=True)
    start_date = serializers.DateField(write_only=True)
    pk = serializers.IntegerField()
    name = serializers.CharField()
    currency = serializers.ChoiceField(choices=constants.CURRENCY_CHOICES)
    reports = ReportItemSerializer(many=True)
