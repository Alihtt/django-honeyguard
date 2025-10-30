"""Tests for Django signals."""

import pytest

from django_honeyguard.signals import honeypot_triggered


class TestHoneypotTriggeredSignal:
    """Test honeypot_triggered signal."""

    def test_signal_exists(self):
        """Test that honeypot_triggered signal exists."""
        assert honeypot_triggered is not None

    @pytest.mark.django_db
    def test_signal_can_be_sent(self):
        """Test that signal can be sent."""
        from django.test import RequestFactory

        def handler(sender, request, data, **kwargs):
            pass

        rf = RequestFactory()
        mock_request = rf.get("/")
        honeypot_triggered.connect(handler)
        honeypot_triggered.send(
            sender=self.__class__, request=mock_request, data={}
        )
        honeypot_triggered.disconnect(handler)

    @pytest.mark.django_db
    def test_signal_receives_correct_data(self):
        """Test that signal receives correct data."""
        from django.test import RequestFactory

        received_data = {}
        received_request = None

        def handler(sender, request, data, **kwargs):
            nonlocal received_data, received_request
            received_data = data
            received_request = request

        honeypot_triggered.connect(handler)

        rf = RequestFactory()
        test_request = rf.get("/admin/")
        test_data = {"username": "test", "password": "pass"}

        honeypot_triggered.send(
            sender=self.__class__, request=test_request, data=test_data
        )

        assert received_data == test_data
        assert received_request == test_request

        honeypot_triggered.disconnect(handler)
