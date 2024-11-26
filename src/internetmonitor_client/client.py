import time
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import boto3

MAX_RESULTS = 1000
ERROR_QUERY_STATUS = "Unable to get query status after {attempts} retries"


class CloudWatchInternetMonitorClient:
    """
    A high-level client representing Amazon CloudWatch Internet Monitor
    """

    def __init__(self, monitor_name: str, **kwargs) -> None:
        self.monitor_name = monitor_name
        self.internetmonitor = boto3.client(
            "internetmonitor",
            **kwargs,
        )

    def get_routing_suggestions(
        self, start_time=None, end_time=None, filter_parameters=None
    )  -> Iterator[dict]:
        """
        Get the predicted average round-trip time (RTT) from an IP prefix toward an AWS location for a DNS resolver.
        """
        resp = self._start_query(
            "ROUTING_SUGGESTIONS", start_time, end_time, filter_parameters
        )
        return self._get_query_results(resp["QueryId"])

    def get_top_locations(self, start_time=None, end_time=None, filter_parameters=None) -> Iterator[dict]:
        """
        Get the availability score, performance score, total traffic, and time to first byte (TTFB) information
        for the top location and ASN combinations that you're monitoring, by traffic volume.
        """
        resp = self._start_query(
            "TOP_LOCATIONS", start_time, end_time, filter_parameters
        )
        return self._get_query_results(resp["QueryId"])

    def get_measurements(self, start_time=None, end_time=None, filter_parameters=None) -> Iterator[dict]:
        """
        Get the availability score, performance score, total traffic, and round-trip times, at 5 minute intervals.
        """
        resp = self._start_query(
            "MEASUREMENTS", start_time, end_time, filter_parameters
        )
        return self._get_query_results(resp["QueryId"])

    def get_overall_traffic_suggestions(
        self, start_time=None, end_time=None, filter_parameters=None
    ) -> Iterator[dict]:
        """
        Get the time to first byte (TTFB), using a 30-day weighted average, for all
        traffic in each AWS location that is monitored.
        """
        resp = self._start_query(
            "OVERALL_TRAFFIC_SUGGESTIONS", start_time, end_time, filter_parameters
        )
        return self._get_query_results(resp["QueryId"])

    def get_overall_traffic_suggestions_details(
        self, start_time=None, end_time=None, filter_parameters=None
    ) -> Iterator[dict]:
        """
        Get the time to first byte (TTFB), using a 30-day weighted average, for each top location,
        for a proposed AWS location.
        """
        resp = self._start_query(
            "OVERALL_TRAFFIC_SUGGESTIONS_DETAILS", start_time, end_time, filter_parameters
        )
        return self._get_query_results(resp["QueryId"])

    def _start_query(
        self, query_type: str, start_time=None, end_time=None, filter_parameters=None
    ):
        if not end_time:
            end_time = datetime.now(UTC)
        if not start_time:
            start_time = end_time + timedelta(days=-1)
        filter_parameters = filter_parameters or []
        return self.internetmonitor.start_query(
            MonitorName=self.monitor_name,
            QueryType=query_type,
            StartTime=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            EndTime=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            FilterParameters=filter_parameters,
        )

    def _wait_for_query_success(self, query_id: str) -> None:
        attempts = 1
        max_attempts = 10
        while attempts <= max_attempts:
            response = self.internetmonitor.get_query_status(
                MonitorName=self.monitor_name,
                QueryId=query_id,
            )
            if response["Status"] == "SUCCEEDED":
                return
            if response["Status"] in ["CANCELED", "FAILED"]:
                break
            time.sleep(0.5)
            attempts += 1

        raise Exception(ERROR_QUERY_STATUS.format(attempts=attempts))

    def _get_query_results(self, query_id: str) -> Iterator[dict]:
        self._wait_for_query_success(query_id)
        next_token = ""
        fields: list = []
        while True:
            response = self.internetmonitor.get_query_results(
                MonitorName=self.monitor_name,
                QueryId=query_id,
                MaxResults=MAX_RESULTS,
                NextToken=next_token,
            )
            next_token = response.get("NextToken") or ""
            if not fields:
                for r in response["Fields"]:
                    fields.append([r["Name"], r["Type"]])
            for row in response.get("Data", []):
                yield self._process_row(row, fields)
            if not next_token:
                break

    def _process_row(self, row: list, fields: list) -> dict:
        record = {}
        for (name, type_), value in zip(fields, row, strict=True):
            if type_ in ["integer", "bigint"]:
                record[name] = int(value)
            elif type_ in ["float", "double"]:
                record[name] = round(float(value), 2)  # type: ignore
            elif type_ == "array" and name == "ipv4_prefixes":
                record[name] = value.strip("[]").split(", ")
            elif type_ == "map"  and name == "fbl_data":
                record[name] = {k: int(v) for k, v in (item.split("=") for item in value.strip("{}").split(", "))}  # type: ignore
            else:
                record[name] = value
        return record
