#!/usr/bin/env python
import argparse
import uuid

from ware_api import DEFAULT_HOST, RecordSort, WareAPI


def main() -> None:
    parser = argparse.ArgumentParser(
        description="""
    # Interact with the Ware GraphQL API
    # To use this tool you must define 2 environment variables (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY).
    # You can get these values from your Ware service representative.
    # """
    )

    parser.add_argument(
        "--endpoint",
        type=str,
        help="Optional endpoint value to override the default",
        default=DEFAULT_HOST,
    )
    parser.add_argument(
        "--zone-id", type=str, help="Zone ID that the query pertains to"
    )
    args = parser.parse_args()

    api = WareAPI(host=args.endpoint)
    # Use JSON format string for the query. It does not need reformatting.

    try:
        # zone_id should be a valid UUID4
        zone_uuid = uuid.UUID(f"urn:uuid:{args.zone_id}")
        more_data = True

        while more_data:
            zone_locations_report_result = api.zone_locations_report(
                str(zone_uuid),
                sort=RecordSort.LATEST,
                record_filter={"statusFilter": []},
            )
            if zone_locations_report_result["status"] != "success":
                print(
                    f"Error calling zoneLocationsReport: "
                    f"{zone_locations_report_result['message']}."
                )
                break
            zone_report_data = zone_locations_report_result["data"]
            print(
                f"zoneLocationReportFound at "
                f"{zone_report_data['zoneInventoryReportUrl']}"
            )

    except TypeError:
        print("Invalid zone_id returned")


if __name__ == "__main__":
    main()
