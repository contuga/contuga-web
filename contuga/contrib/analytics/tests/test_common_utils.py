from datetime import date, datetime

import pytz
from django.test import SimpleTestCase, override_settings

from contuga.contrib.analytics import constants
from contuga.contrib.analytics.utils.common_utils import get_date_limits


class CommonUtilsDateLimitsTestCase(SimpleTestCase):
    @override_settings(TIME_ZONE="Europe/Sofia")
    def test_get_date_limits_uses_local_midnight_for_day_reports(self):
        start_date, end_date = get_date_limits(
            start_date=date(2026, 10, 17),
            end_date=date(2026, 10, 17),
            report_unit=constants.DAYS,
            conf={"default_period": {"days": 7}},
        )

        tzinfo = pytz.timezone("Europe/Sofia")

        self.assertEqual(start_date, tzinfo.localize(datetime(2026, 10, 17, 0, 0, 0)))
        self.assertEqual(
            end_date,
            tzinfo.localize(datetime(2026, 10, 17, 23, 59, 59, 999999)),
        )

    @override_settings(TIME_ZONE="Europe/Sofia")
    def test_get_date_limits_handles_daylight_saving_time_transition_day(self):
        start_date, end_date = get_date_limits(
            start_date=date(2026, 3, 29),
            end_date=date(2026, 3, 29),
            report_unit=constants.DAYS,
            conf={"default_period": {"days": 7}},
        )

        tzinfo = pytz.timezone("Europe/Sofia")

        self.assertEqual(start_date, tzinfo.localize(datetime(2026, 3, 29, 0, 0, 0)))
        self.assertEqual(
            end_date,
            tzinfo.localize(datetime(2026, 3, 29, 23, 59, 59, 999999)),
        )

    @override_settings(TIME_ZONE="UTC")
    def test_get_date_limits_works_for_monthly_ranges(self):
        start_date, end_date = get_date_limits(
            start_date=date(2026, 9, 15),
            end_date=date(2026, 10, 3),
            report_unit=constants.MONTHS,
            conf={"default_period": {"days": 7}},
        )

        tzinfo = pytz.timezone("UTC")

        self.assertEqual(start_date, tzinfo.localize(datetime(2026, 9, 15, 0, 0, 0)))
        self.assertEqual(
            end_date,
            tzinfo.localize(datetime(2026, 10, 3, 23, 59, 59, 999999)),
        )
