import unittest
import os.path
import datetime

import HoursCsvParser

__author__ = 'vsaw'


class TestHoursCsvParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.DATA_ALL_PROJECTS_SINGLE_DAY = os.path.join('test', 'res', 'test-all-projects-single-day.txt')
        cls.DATA_ALL_PROJECTS_SINGLE_DAY_WITH_BLANKS = os.path.join('test', 'res', 'test-all-projects.txt')
        cls.DATA_SINGLE_PROJECT_MULTIPLE_DAYS = os.path.join('test', 'res', 'test-single-project.txt')

    def test_exception_when_file_is_none(self):
        with self.assertRaises(IOError):
            HoursCsvParser.parse(None)

    def test_exception_when_file_does_not_exist(self):
        with self.assertRaises(IOError):
            HoursCsvParser.parse('res/does_not_exist.txt')

    def test_exception_when_file_is_no_file_or_path(self):
        with self.assertRaises(IOError):
            HoursCsvParser.parse(1)

    def test_correct_year_from_header(self):
        result = HoursCsvParser.parse(self.DATA_ALL_PROJECTS_SINGLE_DAY)
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]['date'], datetime.date(2015, 10, 12))

    def test_correct_parse_single_day(self):
        result = HoursCsvParser.parse(self.DATA_ALL_PROJECTS_SINGLE_DAY)
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]['start'], datetime.time(9, 0))
        self.assertEqual(result[0]['finish'], datetime.time(18, 0))
        self.assertEqual(result[0]['pause'], datetime.timedelta(hours=1))
        self.assertEqual(result[0]['total'], datetime.timedelta(hours=8))

    def test_skips_empty_days(self):
        result = HoursCsvParser.parse(self.DATA_ALL_PROJECTS_SINGLE_DAY_WITH_BLANKS)
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]['date'], datetime.date(2015, 10, 12))
        self.assertEqual(result[0]['start'], datetime.time(9, 0))
        self.assertEqual(result[0]['finish'], datetime.time(18, 0))
        self.assertEqual(result[0]['pause'], datetime.timedelta(hours=1))
        self.assertEqual(result[0]['total'], datetime.timedelta(hours=8))

    def test_filter_for_project(self):
        result = HoursCsvParser.parse(self.DATA_ALL_PROJECTS_SINGLE_DAY_WITH_BLANKS, 'project1')
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]['date'], datetime.date(2015, 10, 12))
        self.assertEqual(result[0]['start'], datetime.time(9, 0))
        self.assertEqual(result[0]['finish'], datetime.time(12, 0))
        self.assertEqual(result[0]['pause'], datetime.timedelta(hours=0))
        self.assertEqual(result[0]['total'], datetime.timedelta(hours=3))

    def test_single_project_multiple_day(self):
        result = HoursCsvParser.parse(self.DATA_SINGLE_PROJECT_MULTIPLE_DAYS)

        expected_totals_per_day = [datetime.timedelta(hours=8),
                                   datetime.timedelta(hours=8, minutes=45),
                                   datetime.timedelta(hours=8, minutes=30),
                                   datetime.timedelta(hours=9, minutes=45)]
        self.assertEqual(4, len(result))
        for i in range(len(result)):
            self.assertEqual(expected_totals_per_day[i], result[i]['total'])
