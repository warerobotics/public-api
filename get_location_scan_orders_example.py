#!/usr/bin/env python
import uuid
import json
import argparse
from ware_api import WareAPI, DEFAULT_HOST


def main() -> None:
    parser = argparse.ArgumentParser(
        description="""
    # Interact with the Ware GraphQL API
    # To use this tool you must define 2 environment variables (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY).
    # You can get these values from your Ware service representative.
    # """
    )

    parser.add_argument(
        "--endpoint", type=str, help="Optional endpoint value to override the default", default=DEFAULT_HOST
    )
    parser.add_argument("--zone-id", help="Zone ID for the query", required=True, type=uuid.UUID)
    parser.add_argument("--user-tracking-token", help="Optional user tracking token", default=None)
    parser.add_argument("--status", help="Optional filter for location scan order status", choices=["ERROR", "SUCCEEDED", "QUEUED", "IN_PROGRESS"], default=None)

    args = parser.parse_args()

    api = WareAPI(host=args.endpoint)

    response = api.get_location_scan_orders(str(args.zone_id), args.user_tracking_token, args.status)

    print(json.dumps(response, indent=2))


if __name__ == '__main__':
    main()
