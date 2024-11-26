## Amazon CloudWatch Internet Monitor Client Library for Python

A high-level client representing Amazon CloudWatch Internet Monitor.

## Getting Started

* **Minimum requirements** -- Python 3.11 (or later) and pip
* **Download** -- Download the latest preview release or pick it up from pip:
```
pip install amzn-internetmonitor-client-python
```

## Using the CloudWatch Internet Monitor Client

```python
>>> from internetmonitor_client import CloudWatchInternetMonitorClient
>>> monitor_name  = 'MyVPCMonitor'
>>> client = CloudWatchInternetMonitorClient(monitor_name)

>>> # Get routing suggestions for AS 12345
>>> routing_suggestions = client.get_routing_suggestions(
    filter_parameters=[
        {"Field": "dns_resolver_asn", "Operator": "EQUALS", "Values": ["12345"]},
    ]
)
>>> next(routing_suggestions)
{'dns_resolver_ip': '162.158.197.82', 'dns_resolver_asn': 12345, 'dns_resolver_isp': 'isp name', 'ipv4_prefixes': ['71.134.0.0/15'], 'current_aws_location': 'us-west-2', 'current_latency': 93.4, 'proposed_aws_location': 'us-east-1', 'proposed_latency': 36.2}

>>> # Get suggestions to reduce latency for top locations
>>> top_locations = client.get_top_locations()
>>> next(top_locations)
{'aws_location': 'us-west-2', 'city': 'Berlin', 'metro': 'N/A', 'subdivision': 'Land Berlin', 'country': 'Germany', 'asn': 1234, 'availability': 100.0, 'min_availability': 100.0, 'performance': 100.0, 'min_performance': 100.0, 'bytes_in': 34443600, 'bytes_out': 96288120, 'percentage_of_total_traffic': 0.32, 'current_fbl': 209, 'min_fbl': 206, 'max_fbl': 214, 'best_ec2': 47, 'best_ec2_region': 'eu-central-1', 'best_cf_fbl': 34}

>>> # Get overall traffic suggestions details for us-west-2
>>> traffic_suggestions = client.get_overall_traffic_suggestions_details(
    filter_parameters=[
        {"Field": "current_aws_location", "Operator": "EQUALS", "Values": ["us-west-2"]},
    ]
)
>>> next(traffic_suggestions)
{'city': 'Las Vegas', 'metro': 'Las Vegas', 'subdivision': 'Nevada', 'country': 'United States', 'asn': 1234, 'traffic': 74499564, 'current_aws_location': 'us-west-2', 'fbl_data': {'ap-south-2': 328, 'ap-south-1': 316, 'eu-south-1': 200, 'eu-south-2': 202, 'us-east-1-dfw-2a': 60, 'me-central-1': 307, 'il-central-1': 236, 'ca-central-1': 96, 'us-east-1-atl-2a': 77, 'eu-central-1': 191, 'eu-central-2': 197, 'us-west-1': 34, 'us-west-2': 47, 'af-south-1': 339, 'eu-west-3': 182, 'eu-north-1': 190, 'eu-west-2': 184, 'eu-west-1': 190, 'us-west-2-lax-1b': 33, 'us-west-2-lax-1a': 33, 'ap-northeast-3': 140, 'ap-northeast-2': 159, 'ap-northeast-1': 139, 'me-south-1': 277, 'af-south-1-los-1a': 337, 'sa-east-1': 189, 'us-east-1-qro-1a': 80, 'ap-east-1': 188, 'us-east-1-lim-1a': 171, 'CloudFront': 14, 'ca-west-1': 76, 'ap-southeast-1': 188, 'us-east-1-bue-1a': 228, 'ap-southeast-2': 170, 'ap-southeast-3': 203, 'ap-southeast-4': 182, 'us-east-1': 78, 'ap-southeast-5': 208, 'us-east-2': 72, 'us-east-1-mci-1a': 80, 'us-east-1-mia-2a': 102}}
```

To learn more, visit the Cloud Watch Internet Monitor [user guide documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-IM-view-cw-tools-cwim-query.html).

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
