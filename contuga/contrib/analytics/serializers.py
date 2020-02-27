from rest_framework import serializers

from contuga.contrib.accounts import constants


class ReportSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    income = serializers.DecimalField(max_digits=14, decimal_places=2)
    expenditures = serializers.DecimalField(max_digits=14, decimal_places=2)
    balance = serializers.DecimalField(max_digits=14, decimal_places=2)


class MonthlyReportSerializer(serializers.Serializer):
    start_date = serializers.DateField(write_only=True)
    pk = serializers.IntegerField()
    name = serializers.CharField()
    currency = serializers.ChoiceField(choices=constants.CURRENCY_CHOICES)
    reports = ReportSerializer(many=True)
