import argparse
import uuid
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
    args = parser.parse_args()

    api = WareAPI(host=args.endpoint)
    # Use JSON format string for the query. It does not need reformatting.

    my_info_result = api.my_info()
    if my_info_result["status"] != "success":
        print(f"Error calling myInfo: {my_info_result['message']}.\n"
              "Ensure proper AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set and "
              "configured properly in the Ware portal")
        return

    # Extract the first warehouse zone that was returned, and use it in a query for more detailed information
    zone_id = None
    my_info_data = my_info_result["data"]
    if "organizations" in my_info_data and len(my_info_data["organizations"]) > 0:
        organization_name = my_info_data["organizations"][0]["name"]
        if (
            "warehouses" in my_info_data["organizations"][0]
            and len(my_info_data["organizations"][0]["warehouses"]) > 0
        ):
            warehouse_name = my_info_data["organizations"][0]["warehouses"][0]["name"]
            if (
                "zones" in my_info_data["organizations"][0]["warehouses"][0]
                and len(my_info_data["organizations"][0]["warehouses"][0]["zones"]) > 0
            ):
                zone_id = my_info_data["organizations"][0]["warehouses"][0]["zones"][0]["id"]
                zone_name = my_info_data["organizations"][0]["warehouses"][0]["zones"][0]["name"]
                print(f"Connected to {organization_name}: {warehouse_name}: {zone_name}")
            else:
                print("ERROR: No zones returned")
        else:
            print("ERROR: No warehouses returned")
    else:
        print("ERROR: No organizations returned")

    try:
        # zone_id should be a valid UUID4
        zone_uuid = uuid.UUID(f"urn:uuid:{zone_id}")
        page = 0
        more_data = True
        cursor = None

        while more_data:
            zone_locations_result = api.zone_locations_page(zone_id=str(zone_uuid), page=page, cursor=cursor)
            if zone_locations_result["status"] != "success":
                print(f"Error calling zoneLocationsPage: {zone_locations_result['message']}.")
                break
            zone_locations_data = zone_locations_result["data"]
            for record in zone_locations_data["records"]:
                bin_lpns = []
                for lpn in record["record"]["inventory"]:
                    bin_lpns.append(lpn["lpn"])
                print(f"Bin: {record['record']['binName']} - LPNs: {bin_lpns}")
            if zone_locations_data["pageInfo"]["hasNextPage"]:
                # Ware API uses cursors for paging.  To advance the page, pass the "endCursor" to subsequent calls
                # as the starting cursor.
                cursor = zone_locations_data["pageInfo"]["endCursor"]
                page += 1
            else:
                more_data = False

    except TypeError as e:
        print("Invalid zone_id returned")


if __name__ == "__main__":
    main()
