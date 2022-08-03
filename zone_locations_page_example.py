import argparse
import uuid
from ware_api import Pagination, RecordSort, WareAPI, DEFAULT_HOST


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
    parser.add_argument("--zone_id", type=str, help="Zone ID that the query pertains to")
    args = parser.parse_args()

    api = WareAPI(host=args.endpoint)
    # Use JSON format string for the query. It does not need reformatting.

    try:
        # zone_id should be a valid UUID4
        zone_uuid = uuid.UUID(f"urn:uuid:{args.zone_id}")
        more_data = True
        cursor = None

        while more_data:
            zone_locations_result = api.zone_locations_page(
                str(zone_uuid), 
                cursor,
                Pagination.NEXT,
                RecordSort.LATEST,
                {
                    "statusFilter": []
                }
            )
            if zone_locations_result["status"] != "success":
                print(f"Error calling zoneLocationsPage: {zone_locations_result['message']}.")
                break
            zone_locations_data = zone_locations_result["data"]
            for record in zone_locations_data["records"]:
                bin_lpns = [inventory["lpn"] for inventory in record["record"]["inventory"]]
                print(f"Bin: {record['record']['binName']} - LPNs: {bin_lpns}")
            if zone_locations_data["pageInfo"]["hasNextPage"]:
                # Ware API uses cursors for paging.  To advance the page, pass the "endCursor" to subsequent calls
                # as the starting cursor.
                cursor = zone_locations_data["pageInfo"]["endCursor"]
            else:
                more_data = False

    except TypeError as e:
        print("Invalid zone_id returned")


if __name__ == "__main__":
    main()
