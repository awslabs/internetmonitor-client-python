from unittest.mock import MagicMock, patch

import pytest

from internetmonitor_client import CloudWatchInternetMonitorClient


@patch("internetmonitor_client.client.boto3.client")
class TestCloudWatchInternetMonitorClient:
    def setup_method(self):
        self.monitor_name = "test-monitor"
        self.mock_internetmonitor = MagicMock()

    def test_get_routing_suggestions(self, mock_client):
        mock_client.return_value = self.mock_internetmonitor
        self.mock_internetmonitor.start_query.return_value = {
            "QueryId": "test-query-id"
        }
        self.mock_internetmonitor.get_query_status.return_value = {
            "Status": "SUCCEEDED"
        }
        self.mock_internetmonitor.get_query_results.return_value = {
            "Fields": [
                {"Name": "dns_resolver_asn", "Type": "integer"},
                {"Name": "ipv4_prefixes", "Type": "array"},
                {"Name": "current_latency", "Type": "float"},
                {"Name": "proposed_latency", "Type": "float"},
            ],
            "Data": [
                ["13335", "[85.176.0.0/13]", "100.5", "18.2001"],
            ],
        }

        client = CloudWatchInternetMonitorClient(
            self.monitor_name, region_name="us-west-2"
        )

        routing_suggestions = list(client.get_routing_suggestions())
        assert isinstance(routing_suggestions, list)
        assert len(routing_suggestions) == 1
        assert routing_suggestions[0] == {
            "current_latency": 100.5,
            "proposed_latency": 18.2,
            "dns_resolver_asn": 13335,
            "ipv4_prefixes": ["85.176.0.0/13"],
        }

    def test_get_top_locations(self, mock_client):
        mock_client.return_value = self.mock_internetmonitor
        self.mock_internetmonitor.start_query.return_value = {
            "QueryId": "test-query-id"
        }
        self.mock_internetmonitor.get_query_status.return_value = {
            "Status": "SUCCEEDED"
        }
        self.mock_internetmonitor.get_query_results.return_value = {
            "Fields": [
                {"Name": "asn", "Type": "integer"},
                {"Name": "bytes_in", "Type": "bigint"},
                {"Name": "bytes_out", "Type": "bigint"},
                {"Name": "best_ec2_region", "Type": "string"},
            ],
            "Data": [
                ["7922", "32903724", "26742480", "us-east-1"],
                ["7921", "32903723", "26742481", "us-east-2"],
            ],
        }

        client = CloudWatchInternetMonitorClient(self.monitor_name)

        top_locations = list(client.get_top_locations())
        assert isinstance(top_locations, list)
        assert len(top_locations) == 2
        assert top_locations == [
            {
                "asn": 7922,
                "bytes_in": 32903724,
                "bytes_out": 26742480,
                "best_ec2_region": "us-east-1",
            },
            {
                "asn": 7921,
                "bytes_in": 32903723,
                "bytes_out": 26742481,
                "best_ec2_region": "us-east-2",
            },
        ]

    def test_get_overall_traffic_suggestions(self, mock_client):
        mock_client.return_value = self.mock_internetmonitor
        self.mock_internetmonitor.start_query.return_value = {
            "QueryId": "test-query-id"
        }
        self.mock_internetmonitor.get_query_status.return_value = {
            "Status": "SUCCEEDED"
        }
        self.mock_internetmonitor.get_query_results.return_value = {
            "Fields": [
                {"Name": "current_aws_location", "Type": "string"},
                {"Name": "proposed_aws_location", "Type": "string"},
            ],
            "Data": [],
        }

        client = CloudWatchInternetMonitorClient(self.monitor_name)

        traffic_suggestions = list(client.get_overall_traffic_suggestions())
        assert isinstance(traffic_suggestions, list)
        assert len(traffic_suggestions) == 0

    def test_get_overall_traffic_suggestions_details(self, mock_client):
        mock_client.return_value = self.mock_internetmonitor
        self.mock_internetmonitor.start_query.return_value = {
            "QueryId": "test-query-id"
        }
        self.mock_internetmonitor.get_query_status.return_value = {
            "Status": "SUCCEEDED"
        }
        self.mock_internetmonitor.get_query_results.return_value = {
            "Fields": [
                {"Name": "city", "Type": "string"},
                {"Name": "asn", "Type": "integer"},
                {"Name": "current_aws_location", "Type": "string"},
                {"Name": "fbl_data", "Type": "map"},
            ],
            "Data": [
                [
                    "Ahome",
                    "1399",
                    "us-west-2",
                    "{ap-south-2=334, ap-south-1=340, eu-south-1=208, eu-south-2=196}",
                ],
            ],
        }

        client = CloudWatchInternetMonitorClient(self.monitor_name)

        traffic_suggestions = list(client.get_overall_traffic_suggestions_details())
        assert isinstance(traffic_suggestions, list)
        assert len(traffic_suggestions) == 1
        assert traffic_suggestions[0] == {
            "asn": 1399,
            "city": "Ahome",
            "current_aws_location": "us-west-2",
            "fbl_data": {
                "ap-south-1": 340,
                "ap-south-2": 334,
                "eu-south-1": 208,
                "eu-south-2": 196,
            },
        }

    def test_error_handling(self, mock_client):
        mock_client.return_value = self.mock_internetmonitor
        client = CloudWatchInternetMonitorClient(self.monitor_name)

        def mock_get_query_status(MonitorName, QueryId):  # noqa
            return {"Status": "FAILED"}

        client.internetmonitor.get_query_status.side_effect = mock_get_query_status

        with pytest.raises(
            Exception, match="Unable to get query status after 1 retries"
        ):
            list(client.get_measurements())
