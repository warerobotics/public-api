import argparse
import uuid
import requests
import json
from time import sleep

import websocket

from ware_api import WareAPI, DEFAULT_HOST

api: WareAPI


def main() -> None:
    global api
    parser = argparse.ArgumentParser(
        description="""
    # Upload a WMS data chunk to the Ware GraphQL API.  The data chunk in this example will be read from a file.
    # To use this tool you must define 2 environment variables (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY).
    # You can get these values from your Ware service representative.
    # """
    )

    parser.add_argument(
        "--endpoint", type=str, help="Optional endpoint value to override the default", default=DEFAULT_HOST
    )
    parser.add_argument("--zone_id", type=str, help="Zone ID that the upload pertains to")
    parser.add_argument("--file", type=str, help="Source file name with JSON payload")
    args = parser.parse_args()
    try:
        # zone_id should be a valid UUID4
        zone_uuid = uuid.UUID(f"urn:uuid:{args.zone_id}")
    except TypeError as e:
        print("Invalid zone_id specified")

    api = WareAPI(host=args.endpoint)

    # Load properly formatted JSON with WMS data from the input file
    with open(args.file, "rb") as f:
        json_from_file = json.load(f)

    create_wms_upload_result = api.create_wms_location_history_records(zone_id=args.zone_id, data=json_from_file)
    print(create_wms_upload_result)

    if create_wms_upload_result["status"] != "success":
        print(f"Error calling createWMSLocationHistoryRecords: {create_wms_upload_result['message']}.")
        return

    # Now we can poll for status using the wmsLocationHistoryUploadRecord endpoint
    result = api.wms_location_history_upload_record(create_wms_upload_result["data"]["id"])
    print(result)
    while result["status"] == "success" and result["data"]["status"] not in ["SUCCESS", "FAILURE"]:
        sleep(1)
        result = api.wms_location_history_upload_record(create_wms_upload_result["data"]["id"])
        print(result)


if __name__ == "__main__":
    main()
