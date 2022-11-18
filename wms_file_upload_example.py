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
    # Upload a WMS data file to the Ware GraphQL API
    # To use this tool you must define 2 environment variables (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY).
    # You can get these values from your Ware service representative.
    # """
    )

    parser.add_argument(
        "--endpoint", type=str, help="Optional endpoint value to override the default", default=DEFAULT_HOST
    )
    parser.add_argument("--zone-id", type=str, help="Zone ID that the upload pertains to")
    parser.add_argument("--file", type=str, help="Source file name")
    parser.add_argument("--status-check", type=str, default="subscribe")
    args = parser.parse_args()
    try:
        # zone_id should be a valid UUID4
        zone_uuid = uuid.UUID(f"urn:uuid:{args.zone_id}")
    except TypeError as e:
        print("Invalid zone_id specified")

    api = WareAPI(host=args.endpoint)

    # Prepare a file upload request
    file_format = "CSV"
    if args.file.lower().endswith("xlsx"):
        file_format = "XLSX"
    create_wms_upload_result = api.create_wms_location_history_upload(zone_id=args.zone_id, file_format=file_format)
    print(create_wms_upload_result)

    if create_wms_upload_result["status"] != "success":
        print(f"Error calling createWMSLocationHistoryUpload: {create_wms_upload_result['message']}.")
        return

    with open(args.file, "rb") as f:
        files = {"file": (args.file, f)}
        fields_dict = json.loads(create_wms_upload_result["data"]["uploadFields"])
        http_response = requests.post(create_wms_upload_result["data"]["uploadUrl"], data=fields_dict, files=files)

    # If successful, returns HTTP status code 204
    print(f"File upload HTTP status code: {http_response.status_code}")

    if args.status_check == "poll":
        # Now we can poll for status using the wmsLocationHistoryUploadRecord endpoint
        result = api.wms_location_history_upload_record(create_wms_upload_result["data"]["id"])
        print(result)
        while result["status"] == "success" and result["data"]["status"] not in ["SUCCESS", "FAILURE"]:
            sleep(1)
            result = api.wms_location_history_upload_record(create_wms_upload_result["data"]["id"])
            print(result)
    elif args.status_check == "subscribe":
        # Use the GraphQL subscribe mechanism to wait for updates
        # The following call will block and wait on the websocket used for the subscription.
        # Any data received will be handled by the handler function that is passed in
        api.subscribe_wms_location_history_upload_status_change(
            create_wms_upload_result["data"]["id"], data_handler=wms_upload_subscription_data_handler
        )


def wms_upload_subscription_data_handler(ws: websocket.WebSocket, message: str) -> None:
    #  Message will arrive in the format:
    # {
    #   "id": SUBSCRIPTION_ID,
    #   "type": "data",
    #   "payload": {"data": { DATA_RETURNED_FROM_API } }
    # }
    global api
    print(f"data message: {message}")
    message_object = json.loads(message)
    subscription_data = message_object["payload"]["data"]["subscribeWMSLocationHistoryUploadStatusChange"]
    if subscription_data["status"] in ["SUCCESS", "FAILURE"]:
        # Gracefully end the subscription
        api.unsubscribe(message_object["id"], ws)


if __name__ == "__main__":
    main()
