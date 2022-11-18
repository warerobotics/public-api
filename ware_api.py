import os
import json
import requests
from enum import Enum
from typing_extensions import NotRequired
from typing import Dict, Optional, Callable, List, TypedDict

import websocket
from requests_aws4auth import AWS4Auth
from requests import Response

from ware_subscription_client import subscribe, unsubscribe
from queries import (
    my_info as my_info_query,
    get_zone_locations as get_zone_locations_query,
    get_zone_locations_report as get_zone_locations_report_query,
    get_location_scan_order as get_location_scan_order_query,
    get_location_scan_orders as get_location_scan_orders_query,
    get_wms_location_history_upload_record as get_wms_location_history_upload_record_query,
)
from mutations import (
    create_wms_location_history_records as create_wms_location_history_records_mutation,
    create_wms_location_history_upload as create_wms_location_history_upload_mutation,
    reset_drone_required_action as reset_drone_required_action_mutation,
    create_location_scan_order as create_location_scan_order_mutation,
)
from subscriptions import (
    wms_location_history_upload_status_change as wms_location_history_upload_status_change_subscription,
    location_scan_orders as location_scan_orders_subscription,
)

AWS_SERVICE = "appsync"
JSON_CONTENT_TYPE = "application/json"
DEFAULT_REGION = "us-east-1"
DEFAULT_HOST = "iqiurguobbaotjtnrffqnx7zmu.appsync-api.us-east-1.amazonaws.com"


class Pagination(str, Enum):  # same as graphql enum
    NEXT = "NEXT"
    PREV = "PREV"


class StatusFilter(str, Enum):
    EXCEPTION = "EXCEPTION"
    AUDIT = "AUDIT"
    RESOLVED = "RESOLVED"


class RecordSearchType(str, Enum):
    LPN = "LPN"
    LOCATION = "LOCATION"


class RecordSort(str, Enum):
    AISLE = "AISLE"
    LATEST = "LATEST"


class ReportFormat(str, Enum):
    CSV = "CSV"
    XLSX = "XLSX"


class LocationFilterV2(TypedDict):
    searchString: NotRequired[str]
    searchType: NotRequired[RecordSearchType]
    aisleStart: NotRequired[int]
    aisleEnd: NotRequired[int]
    occupancy: NotRequired[bool]
    locationScanOrderId: NotRequired[str]
    statusFilter: List[StatusFilter]


class WareAPI:
    def __init__(self, host: str = DEFAULT_HOST, region: str = DEFAULT_REGION):
        self.host = host
        self.region = region
        self.amz_target = ""
        self.ware_api_url = f"https://{self.host}/graphql"

        # Retrieve access keys
        self.access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        self.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        if self.access_key is None or self.secret_key is None:
            raise Exception("Must define access key and secret key")

        self.session = requests.Session()
        self.session.auth = AWS4Auth(self.access_key, self.secret_key, region, AWS_SERVICE)


    def query(self, query: str, data_key: str, variables: Optional[Dict] = None) -> Response:
        """ Generic GraphQL query method. Does an HTTP POST with the query and variables as parameters """
        variables = variables or {}

        response: Response = self.session.request(
            url=self.ware_api_url,
            method="POST",
            json={
                "query": query,
                "variables": variables
            },
        )

        try:
            response.raise_for_status()
        except:
            return {
                "status": "error",
                "message": f"HTTP error: {response.status_code}",
                "response": response.json(),
            }

        response = response.json()

        if (data := response.get("data")) is not None:
            return {
                "status": "success",
                "data": data[data_key],
            }

        return {
            "status": "error",
            "message": response["message"],
            "response": response,
        }


    def my_info(self) -> Dict:
        return self.query(my_info_query, "myInfo")


    def zone_locations_page(
            self,
            zone_id: str,
            limit: int = 10,
            cursor: Optional[str] = None,
            paginate: Pagination = Pagination.NEXT,
            sort: RecordSort = RecordSort.LATEST,
            record_filter: Optional[LocationFilterV2] = None
    ) -> Dict:
        variables = {
            "zoneId": zone_id,
            "sort": sort.value,
            "paginate": paginate.value,
            "limit": limit,
            "cursor": cursor,
        }

        if record_filter:
            variables["filter"] = record_filter

        return self.query(get_zone_locations_query, "zoneLocationsPageV2", variables=variables)


    def zone_locations_report(
        self,
        zone_id: str,
        sort: RecordSort = RecordSort.LATEST,
        report_format: ReportFormat = ReportFormat.CSV,
        record_filter: Optional[LocationFilterV2] = None,
    ) -> Dict:
        variables = {
            "zoneId": zone_id,
            "sort": sort.value,
            "filter": record_filter,
            "reportFormat": report_format.value,
        }

        if record_filter:
            variables["filter"] = record_filter

        return self.query(zone_locations_report_query, "zoneLocationsReport", variables=variables)


    def create_wms_location_history_upload(self, zone_id: str, file_format: Optional[str]="csv") -> Dict:
        if file_format:
            file_format = file_format.upper()
        else:
            file_format = "CSV"

        variables = {
            "zoneId": zone_id,
            "fileFormat": file_format
        }

        return self.query(
            create_wms_location_history_upload_mutation,
            "createWMSLocationHistoryUpload",
            variables=variables,
        )


    def create_wms_location_history_records(self, zone_id: str, data: Dict[str, str]) -> Dict:
        variables = {
            "zoneId": zone_id,
            "records": data
        }

        return self.query(
            create_wms_location_history_records_mutation,
            "createWMSLocationHistoryRecords",
            variables=variables,
        )


    def get_wms_location_history_upload_record(self, record_id: str) -> Dict:
        variables = { "id": record_id }
        return self.query(
            get_wms_location_history_upload_record_query,
            "wmsLocationHistoryUploadRecord",
            variables=variables
        )


    def subscribe_wms_location_history_upload_status_change(self, record_id: str, data_handler: Callable) -> None:
        subscribe(
            aws_access_key=self.access_key,
            aws_secret_key=self.secret_key,
            api_url=self.ware_api_url,
            subscription=wms_location_history_upload_status_change_subscription,
            subscription_variables={ "id", record_id },
            data_handler=data_handler,
        )


    def subscribe_location_scan_orders(self, zone_id: str, data_handler: Callable):
        subscribe(
            aws_access_key=self.access_key,
            aws_secret_key=self.secret_key,
            api_url=self.ware_api_url,
            subscription=location_scan_orders_subscription,
            subscription_variables={ "zoneId": zone_id },
            data_handler=data_handler,
        )


    @staticmethod
    def unsubscribe(subscription_id: str, web_socket: websocket.WebSocket) -> None:
        unsubscribe(subscription_id, web_socket)


    def reset_drone_required_action(self, required_action_id: str) -> Dict:
        variables = { 'requiredActionId': required_action_id }
        return self.query(reset_drone_required_action_mutation, "resetDroneRequiredAction", variables=variables)


    def create_location_scan_order(self, zone_id: str, bins: List[str], user_tracking_token: Optional[str] = None) -> Dict:
        variables = {
            "bins": bins,
            "zoneId": zone_id,
            "userTrackingToken": user_tracking_token,
        }

        return self.query(
            create_location_scan_order_mutation,
            "createLocationScanOrder",
            variables=variables
        )


    def get_location_scan_order(self, location_scan_order_id: str) -> Dict:
        variables = { "id": location_scan_order_id }
        return self.query(get_location_scan_order_query, "getLocationScanOrder", variables=variables)


    def get_location_scan_orders(self, zone_id: str, user_tracking_token: Optional[str] = None, status: Optional[str] = None) -> Dict:
        variables = {
            "zoneId": zone_id,
            "status": status,
            "userTrackingToken": user_tracking_token,
        }

        self.query(get_location_scan_orders_query, "getLocationScanOrders", variables=variables)
