from typing_extensions import NotRequired
import requests
import os
import json
from enum import Enum
from typing import Dict, Optional, Callable, List, TypedDict

import websocket
from requests_aws4auth import AWS4Auth
from requests import Response

from ware_subscription_client import subscribe, unsubscribe

JSON_CONTENT_TYPE = "application/json"
AWS_SERVICE = "appsync"
DEFAULT_HOST = "iqiurguobbaotjtnrffqnx7zmu.appsync-api.us-east-1.amazonaws.com"
DEFAULT_REGION = "us-east-1"

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

    def _extract_json_response(self, raw_response: Response, data_key: str) -> dict:
        if raw_response.status_code == 200:
            json_response = json.loads(raw_response.content)
            if (data := json_response.get("data")) is not None and data.get(data_key) is not None:
                return {"status": "success", "data": json_response["data"][data_key]}

        return {
            "status": "error",
            "message": f"Problem loading response data for {data_key}",
            "response": raw_response.json(),
        }

    def my_info(self) -> Dict:
        query = """
            query GetUser {
              myInfo {
                organizations {
                  name
                  warehouses {
                    id
                    name
                    zones {
                      aisles
                      id
                      name
                    }
                  }
                }
              }
            }
            """
        raw_response = self.query(query=query)
        return self._extract_json_response(raw_response, "myInfo")

    def zone_locations_page(
            self,
            zone_id: str,
            cursor: Optional[str] = None,
            paginate: Pagination = Pagination.NEXT,
            sort: RecordSort = RecordSort.LATEST,
            record_filter: Optional[LocationFilterV2] = None
    ) -> Dict:
        query = """
    query getZoneLocations(
        $zoneId: String!,
        $limit: Int,
        $cursor: String,
        $paginate: Pagination,
        $sort: RecordSort,
        $filter: LocationFilterV2
    ) {
        zoneLocationsPageV2 (
            zoneId: $zoneId,
            limit: $limit,
            cursor: $cursor,
            paginate: $paginate,
            sort: $sort,
            filter: $filter
        ) {
            zoneId
            timezone
            records {
                cursor
                record {
                    id
                    aisle
                    binName
                    sharedLocationViewUrl
                    inventory {
                        lpn
                        exceptions {
                            type
                            parameters {
                                lpn
                                wmsReportedLpns	
                            }
                            exceptionHistory {
                                userStatus
                                timestamp
                            }
                        }
                    }
                    exceptions {
                        type
                        parameters {
                            lpn
                            wmsReportedLpns	
                        }
                        exceptionHistory {
                            userStatus
                            timestamp
                        }
                    }
                }
            }
            pageInfo {
                totalRecords
                startIndex
                startCursor
                endCursor
                hasNextPage
                hasPrevPage
            }
        }
    }
        """
        variables = {
            "zoneId": zone_id,
            "sort": sort,
            "paginate": paginate,
            "limit": 10,
            "cursor": cursor,
        }
        if record_filter:
            variables["filter"] = record_filter

        raw_response = self.query(query=query, variables=variables)
        return self._extract_json_response(raw_response, "zoneLocationsPageV2")

    def zone_locations_report(
            self,
            zone_id: str,
            sort: RecordSort = RecordSort.LATEST,
            record_filter: Optional[LocationFilterV2] = None
    ) -> Dict:
        query = """
    query getZoneLocationReport(
        $zoneId: String!, 
        $sort: RecordSort, 
        $filter: LocationFilterV2
    ) {
        zoneLocationsReport(zoneId: $zoneId, sort: $sort, filter: $filter) {
            zoneInventoryReportUrl
        }
    }
        """
        variables = {
            "zoneId": zone_id,
            "sort": sort,
        }
        if record_filter:
            variables["filter"] = record_filter

        raw_response = self.query(query=query, variables=variables)
        return self._extract_json_response(raw_response, "zoneLocationsReport")

    def create_wms_location_history_upload(self, zone_id: str, file_format: Optional[str]="csv") -> Dict:
        if file_format:
            file_format = file_format.upper()
        else:
            file_format = "CSV"

        mutation = """
            mutation CreateWMSLocationHistoryUpload($zoneId: String!, $fileFormat: WMSUploadFormat) {
                createWMSLocationHistoryUpload(zoneId: $zoneId, format: $fileFormat) {
                    id
                    uploadFields
                    uploadUrl
                }
            }
        """
        variables = {"zoneId": zone_id, "fileFormat": file_format}
        raw_response = self.query(query=mutation, variables=variables)
        return self._extract_json_response(raw_response, "createWMSLocationHistoryUpload")

    def create_wms_location_history_records(self, zone_id: str, data: Dict[str, str]) -> Dict:
        mutation = """
            mutation CreateWMSLocationHistoryRecords($zoneId: String!, $records: [WMSLocationHistoryRecord]!) {
                createWMSLocationHistoryRecords(zoneId: $zoneId, records: $records) {
                    id
                    uploadFields
                    uploadUrl
                }
            }
        """
        variables = {"zoneId": zone_id, "records": data}
        raw_response = self.query(query=mutation, variables=variables)
        return self._extract_json_response(raw_response, "createWMSLocationHistoryRecords")

    def wms_location_history_upload_record(self, record_id: str) -> Dict:
        query = """
            query WmsLocationHistoryUploadRecord($id: String!) {
              wmsLocationHistoryUploadRecord(id: $id) {
                created
                failedRecords
                id
                processedRecords
                skippedRecords
                status
                totalRecords
                updated
                userId
                zoneId
              }
            }
        """
        variables = {"id": record_id}
        raw_response = self.query(query=query, variables=variables)
        return self._extract_json_response(raw_response, "wmsLocationHistoryUploadRecord")

    def query(self, query: str, variables: Optional[Dict] = None) -> Response:
        """ Generic GraphQL query method. Does an HTTP POST with the query and variables as parameters """
        if variables is None:
            variables = dict()
        response = self.session.request(
            url=self.ware_api_url,
            method="POST",
            json={"query": query, "variables": variables},
        )
        return response

    def subscribe_wms_location_history_upload_status_change(self, record_id: str, data_handler: Callable) -> None:
        query = """
            subscription SubscribeWMSLocationHistoryUploadStatusChange($id: String!) {
              subscribeWMSLocationHistoryUploadStatusChange(id: $id) {
                created
                failedRecords
                id
                processedRecords
                skippedRecords
                status
                totalRecords
                updated
                userId
                zoneId
              }
            }
        """
        variables = {"id": record_id}
        subscribe(
            aws_access_key=self.access_key,
            aws_secret_key=self.secret_key,
            api_url=self.ware_api_url,
            subscription=query,
            subscription_variables=variables,
            data_handler=data_handler,
        )

    def subscribe_location_scan_orders(self, zone_id: str, data_handler: Callable):
        query = """
            subscription SubscribeLocationScanOrders($zoneId: String!) {
              subscribeLocationScanOrders(zoneId: $zoneId) {
                zoneId
                userTrackingToken
                status
                orders {
                  bins {
                    error {
                      id
                      message
                      timestamp
                      type
                    }
                    id
                    record {
                      aisle
                      binName
                      exceptions {
                        description
                        type
                      }
                      inventory {
                        lpn
                        recordId
                      }
                      recordId
                      sharedLocationViewUrl
                      timestamp
                      userStatus
                    }
                    status
                  }
                  endTime
                  createdAt
                  id
                  startTime
                  status
                  userTrackingToken
                  zoneId
                }
              }
            }
        """

        variables = {
            "zoneId": zone_id,
        }

        subscribe(
            aws_access_key=self.access_key,
            aws_secret_key=self.secret_key,
            api_url=self.ware_api_url,
            subscription=query,
            subscription_variables=variables,
            data_handler=data_handler,
        )

    def reset_required_action(self, required_action_id: str) -> Dict:
        mutation = """
          mutation ResetDroneRequiredAction($requiredActionId: String!) {
            resetDroneRequiredAction(requiredActionId: $requiredActionId) {
              nests {
                drone {
                  id
                  requiredActions {
                    id
                    action
                    shortName
                    description
                  }
                }
              }
            }
          }
        """
        variables = {'requiredActionId': required_action_id}
        raw_response = self.query(query=mutation, variables=variables)
        return self._extract_json_response(raw_response, "resetDroneRequiredAction")

    @staticmethod
    def unsubscribe(subscription_id: str, web_socket: websocket.WebSocket) -> None:
        unsubscribe(subscription_id, web_socket)

    def create_location_scan_order(self, zone_id: str, bins: List[str], user_tracking_token: Optional[str] = None) -> Dict:
        mutation = """
            mutation CreateLocationScanOrder($zoneId: String!, $bins: [String!]!, $userTrackingToken: String) {
              createLocationScanOrder(zoneId: $zoneId, bins: $bins, userTrackingToken: $userTrackingToken) {
                id
                createdAt
                userTrackingToken
              }
            }
        """

        variables = {
            "zoneId": zone_id,
            "bins": bins,
            "userTrackingToken": user_tracking_token,
        }

        return self._extract_json_response(
            self.query(query=mutation, variables=variables), "createLocationScanOrder"
        )

    def get_location_scan_order(self, location_scan_order_id: str) -> Dict:
        query = """
            query GetLocationScanOrder($id: String!) {
              getLocationScanOrder(id: $id) {
                bins {
                  error {
                    id
                    message
                    timestamp
                    type
                  }
                  id
                  record {
                    aisle
                    binName
                    exceptions {
                      description
                      type
                    }
                    inventory {
                      lpn
                      recordId
                    }
                    recordId
                    sharedLocationViewUrl
                    timestamp
                    userStatus
                  }
                  status
                }
                endTime
                createdAt
                id
                startTime
                status
                userTrackingToken
                zoneId
              }
            }
        """

        variables = { "id": location_scan_order_id }

        return self._extract_json_response(
            self.query(query=query, variables=variables), "getLocationScanOrder"
        )

    def get_location_scan_orders(self, zone_id: str, user_tracking_token: Optional[str] = None, status: Optional[str] = None) -> Dict:
        query = """
            query GetLocationScanOrders($zoneId: String!, $userTrackingToken: String, $status: String) {
              getLocationScanOrders(id: $id, userTrackingToken: $userTrackingToken, status: $status) {
                zoneId
                userTrackingToken
                status
                orders {
                  bins {
                    error {
                      id
                      message
                      timestamp
                      type
                    }
                    id
                    record {
                      aisle
                      binName
                      exceptions {
                        description
                        type
                      }
                      inventory {
                        lpn
                        recordId
                      }
                      recordId
                      sharedLocationViewUrl
                      timestamp
                      userStatus
                    }
                    status
                  }
                  endTime
                  createdAt
                  id
                  startTime
                  status
                  userTrackingToken
                  zoneId
                }
              }
            }
        """

        variables = {
            "zoneId": zone_id,
            "status": status,
            "userTrackingToken": user_tracking_token,
        }

        return self._extract_json_response(
            self.query(query=query, variables=variables), "getLocationScanOrders"
        )
