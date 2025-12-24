"""Tests for utility functions."""

import pytest
from datetime import datetime
from src.utils import (
    format_hours, format_number, parse_iso_date,
    get_year_from_date, get_month_key
)


class TestFormatHours:
    def test_simple(self):
        assert format_hours(1.5) == "1,5"
    
    def test_thousands(self):
        assert format_hours(1234.5) == "1.234,5"
    
    def test_zero(self):
        assert format_hours(0) == "0,0"
    
    def test_large(self):
        assert format_hours(12345.6) == "12.345,6"


class TestFormatNumber:
    def test_simple(self):
        assert format_number(123) == "123"
    
    def test_thousands(self):
        assert format_number(1234) == "1.234"
    
    def test_millions(self):
        assert format_number(1234567) == "1.234.567"
    
    def test_zero(self):
        assert format_number(0) == "0"


class TestParseIsoDate:
    def test_valid_z(self):
        result = parse_iso_date("2024-01-15T10:30:00Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    def test_valid_offset(self):
        result = parse_iso_date("2024-06-20T15:45:00+00:00")
        assert result is not None
        assert result.year == 2024
    
    def test_null_date(self):
        assert parse_iso_date("0001-01-01T00:00:00Z") is None
    
    def test_empty(self):
        assert parse_iso_date("") is None
        assert parse_iso_date(None) is None
    
    def test_invalid(self):
        assert parse_iso_date("not-a-date") is None


class TestGetYearFromDate:
    def test_valid(self):
        assert get_year_from_date("2024-01-15T10:30:00Z") == "2024"
    
    def test_short(self):
        assert get_year_from_date("abc") is None
    
    def test_empty(self):
        assert get_year_from_date("") is None
        assert get_year_from_date(None) is None


class TestGetMonthKey:
    def test_valid(self):
        assert get_month_key("2024-06-15T10:30:00Z") == "2024-06"
    
    def test_invalid(self):
        assert get_month_key("invalid") is None
    
    def test_null_date(self):
        assert get_month_key("0001-01-01T00:00:00Z") is None

