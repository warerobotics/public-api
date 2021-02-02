import requests
import os
import json
from typing import Any, Dict, Optional
from requests_aws4auth import AWS4Auth
from requests import Response

JSON_CONTENT_TYPE = "application/json"
AWS_SERVICE = "appsync"
DEFAULT_HOST = "iqiurguobbaotjtnrffqnx7zmu.appsync-api.us-east-1.amazonaws.com"
DEFAULT_REGION = "us-east-1"


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

        return {"status": "error", "message": f"Problem loading response data for {data_key}"}

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

    def zone_locations_page(self, zone_id: str, page: int = 0, cursor: Optional[Any] = None) -> Dict:
        query = """
            query GetZoneLocations($zoneId: String!, $limit: Int, $filter: LocationFilter, $cursor: String, $page: Pagination) {
                zoneLocationsPage(zoneId: $zoneId, limit: $limit, filter: $filter, cursor: $cursor, paginate: $page) {
                    zoneId
                    timezone
                    records {
                        record {
                            recordId
                            aisle
                            binName
                            timestamp
                            inventory {
                                lpn
                            }
                            exceptions {
                                type
                                description
                            }
                            userStatus
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
            "limit": 10,
            "pageIndex": page,
            "filter": {"aisleStart": None, "aisleEnd": None, "statusFilter": []},
            "cursor": cursor,
        }
        raw_response = self.query(query=query, variables=variables)
        return self._extract_json_response(raw_response, "zoneLocationsPage")

    def query(self, query: str, variables: Optional[Dict] = None) -> Response:
        # Now we can simply post the request...
        if variables is None:
            variables = dict()
        response = self.session.request(
            url=self.ware_api_url,
            method="POST",
            json={"query": query, "variables": variables},
        )
        return response
