# Introduction to the Ware API

The Ware API understands [GraphQL](https://graphql.org/). GraphQL is a query language for APIs that provides a complete
and understandable description of the data in the API, and gives clients the power to ask for exactly what they need and
nothing more. There are several popular Python libraries for GraphQL, however the included example relies on directly
POSTing GraphQL queries to the endpoint. For demonstration purposes, each of the supported queries are included in
the `WareAPI` class contained in the `ware_api.py` file. The `call.py`
file demonstrates basic usage of the example class, and you are free to experiment using the provided documentation as a
guide.

# Endpoint

The endpoint for Ware's API is:

https://iqiurguobbaotjtnrffqnx7zmu.appsync-api.us-east-1.amazonaws.com/graphql

Calls to the endpoint must be signed for them to be allowed through. The signature process is the same as that used by
AWS when authenticating using IAM. The appropriate Access Key ID and Secret Access Key will be provided to you by Ware.
The `ware_api.py` script included with these docs details the procedure needed to call the API. This script leverages
the `requests` and `AWS4Auth` libraries. A sample `requirements.txt` file is included as well.

# Schema

Please refer to the `ware_schema.graphql` file for a complete schema definition of available endpoints in the Ware API.

# Queries

## Api List

- [myInfo](###myinfo)
- [zoneLocationsPageV2](###zoneLocationsPageV2)
- [
createWMSLocationHistoryUpload\
CreateWMSLocationHistoryRecords\
WmsLocationHistoryUploadRecord\
SubscribeWMSLocationHistoryUploadStatusChange](##WMSDataUpload)
- [ResetDroneRequiredAction](###Clear/reset\ a\ required\ action)
- [CreateLocationScanOrder](###createLocationScanOrder)
- [GetLocationScanOrder](###getLocationScanOrder)
- [GetLocationScanOrders](###getLocationScanOrders)

## Techniques
- [Result Paging](##ResultPaging)

## Deprecated
- [zoneLocationsPage](###zoneLocationsPage)

---

## Self

### myInfo

**Description:**
The myInfo query takes no parameters and will return information about all of the Organizations, Warehouses, and Zones
that the user has access to. This information, specifically the zone `id` value, will be a critical when querying other
aspects of the API.

**Request:**

```graphql
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
```

**Response:**
The Ware API myInfo endpoint will return a JSON string in the manner requested by the client that will resemble the
following:

```json
{
  "data": {
    "myInfo": {
      "organizations": [
        {
          "name": "Sample Organization",
          "warehouses": [
            {
              "id": "5a74c428-4444-4e05-b1d2-0a07ed046b4a",
              "name": "123 Sample Rd.",
              "zones": [
                {
                  "aisles": [
                    "A",
                    "B",
                    "C"
                  ],
                  "id": "dc293630-62cd-404b-ae09-8914b4426297",
                  "name": "Sample Zone",
                  "organizationName": "Sample Organization",
                  "warehouseName": "123 Sample Rd."
                }
              ]
            }
          ]
        }
      ]
    }
  }
}
```

## Inventory and Location Information

### zoneLocationsPageV2
**Description:**
The zoneLocationsPageV2 query expects a required parameter for `zone_id` and several optional parameters that control 
data page size, paging options, sorting direction and filter parameters. This query can be used to determine what LPNs 
have last been detected in the specified zone by the Ware system.

**Request**
```graphql
query GetInventoryPage(
  $zoneId: String!
  $limit: Int
  $filter: LocationFilterV2
  $cursor: String
  $page: Pagination
  $sort: RecordSort
) {
  zoneLocationsPageV2(
    zoneId: $zoneId
    limit: $limit
    cursor: $cursor
    paginate: $page
    filter: $filter
    sort: $sort
  ) {
    zoneId
    records {
      cursor
      record {
        id
        aisle
        binName
        timestamp
        inventory {
          id
          lpn
          exceptions {
            id
            type
            exceptionHistory {
              userStatus
            }
            parameters {
              lpn
            }
          }
        }
        exceptions {
          id
          type
          exceptionHistory {
            userStatus
          }
          parameters {
            lpn
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
```

**Response**
```json
{
  "data": {
    "zoneLocationsPageV2": {
      "zoneId": "bff4611f-a9f2-4b8b-abeb-99ea6b6a55f0",
      "timezone": "UTC",
      "records": [
        {
          "cursor": "{\"iso_time\": \"2022-06-08T23:31:54.326421\", \"aisle_index\": 1, \"bin_index\": 30000, \"bh_id\": \"a6cf6caa-b56f-406f-9108-c0691abfb4dc\", \"filter\": {\"search_string\": null, \"search_type\": null, \"aisle_start\": null, \"aisle_end\": null, \"occupancy\": null, \"location_scan_order_id\": null, \"status_filter\": [\"EXCEPTION\"]}}",
          "record": {
            "id": "a6cf6caa-b56f-406f-9108-c0691abfb4dc",
            "aisle": "A",
            "binName": "A-03-W-1",
            "timestamp": "2022-06-08T23:36:31+00:00",
            "inventory": [
              {
                "id": "a3af04e2-4ce4-49c8-a6b8-d5fda92d5afd",
                "lpn": "W-10001268",
                "exceptions": []
              }
            ],
            "exceptions": [
              {
                "id": "a77af534-928c-4f01-be92-784ce61172b6",
                "exceptionHistory": [
                  {
                    "userStatus": null
                  }
                ],
                "parameters": {
                  "lpn": [
                    "W-10001268"
                  ]
                }
              }
            ]
          }
        }
      ],
      "pageInfo": {
        "totalRecords": 4,
        "startIndex": 0,
        "startCursor": "{\"iso_time\": \"2022-06-08T23:31:54.326421\", \"aisle_index\": 1, \"bin_index\": 30000, \"bh_id\": \"a6cf6caa-b56f-406f-9108-c0691abfb4dc\", \"filter\": {\"search_string\": null, \"search_type\": null, \"aisle_start\": null, \"aisle_end\": null, \"occupancy\": null, \"location_scan_order_id\": null, \"status_filter\": [\"EXCEPTION\"]}}",
        "endCursor": "{\"iso_time\": \"2022-06-08T23:31:54.326421\", \"aisle_index\": 1, \"bin_index\": 30000, \"bh_id\": \"a6cf6caa-b56f-406f-9108-c0691abfb4dc\", \"filter\": {\"search_string\": null, \"search_type\": null, \"aisle_start\": null, \"aisle_end\": null, \"occupancy\": null, \"location_scan_order_id\": null, \"status_filter\": [\"EXCEPTION\"]}}",
        "hasNextPage": true,
        "hasPrevPage": false
      }
    }
  }
}
```

### zoneLocationsReport
**Description:**
The zoneLocationsReport query expects a required parameter for `zone_id` and several optional parameters that control 
data sorting direction and filter parameters. The report in this query can be used to determine what LPNs have last 
been detected in the specified zone by the Ware system.

**Request**
```gql
query GetInventoryPage(
    $zoneId: String!,$filter:LocationFilterV2,  $sort: RecordSort, $format: SpreadsheetFormat,
) {
  zoneLocationsReport(zoneId: $zoneId, filter: $filter, sort: $sort, reportFormat: $format) {
    zoneInventoryReportUrl
  }
}
```

**Response**
```json
{
  "data": {
    "zoneLocationsReport": {
      "zoneInventoryReportUrl": "https://foobar.com/foo.xlsx"
    }
  }
}
```



### zoneLocationsPage
**Deprication**
This API is being deprecated in favor of the new
[unified location and inventory query](###zoneLocationsPageV2)

**Description:**
The zoneLocationsPage query expects a required parameter for `zone_id` and several optional parameters that control data
page size, paging options, and filter parameters. This query can be used to determine what LPNs have last been detected
in the specified zone by the Ware system.

**Request:**

```graphql
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
               sharedLocationViewUrl
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
```

**Response:**
The Ware API zoneLocationsPage endpoint will return a JSON string in the manner requested by the client that will
resemble the following:

```json
{
  "data": {
    "zoneLocationsPage": {
      "zoneId": "dc293630-62cd-404b-ae09-8914b4426297",
      "timezone": "UTC",
      "records": [
        {
          "record": {
            "recordId": "87dc1d3e-90d2-463c-b78c-50e6d9273b35",
            "aisle": "C",
            "binName": "C101B02",
            "timestamp": "2020-06-16T23:15+00:00",
            "inventory": [
              {
                "lpn": "12360901-ui"
              }
            ],
            "exceptions": [],
            "userStatus": null,
            "sharedLocationViewUrl": ""
          }
        },
        ...
      ],
      "pageInfo": {
        "totalRecords": 10065,
        "startIndex": 0,
        "startCursor": "{\"aisle_index\": 1, \"bin_index\": 10201, \"bh_id\": \"96eb1fe9-27ba-42c6-b7dc-486a3f2bfdd4\", \"filter\": {\"location_name\": null, \"aisle_start\": null, \"aisle_end\": null, \"occupancy\": null, \"status_filter\": []}}",
        "endCursor": "{\"aisle_index\": 1, \"bin_index\": 30202, \"bh_id\": \"7dc5ddc0-ca81-4bb7-9134-630cd1f8b00e\", \"filter\": {\"location_name\": null, \"aisle_start\": null, \"aisle_end\": null, \"occupancy\": null, \"status_filter\": []}}",
        "hasNextPage": true,
        "hasPrevPage": false
      }
    }
  }
}
```

## Result Paging

All potentially large responses exposed by the Ware API utilize GraphQL [Paging](https://graphql.org/learn/pagination/)
techniques. Ware pagination in GraphQL is cursor-based and that cursor information is returned with each response. This
allows support for the dynamic addition of records to the database while a user paginated bi-directionally through the
records in the UI. With this in mind, it is important to remember that new records can be inserted both before and after
the current result, and the record that a cursor references can be deleted. However, cursors are still valid for
pagination even if the underlying records are deleted.

Within the `pageInfo` element there are key/value pairs for the cursor extents that represent the beginning and end of
the data that was returned, along with any filter parameters that were used to compose the result. The start and end
cursor values are returned as `startCursor` and `endCursor` respectively. The values in these fields are able to be
passed as the `cursor` variable to subsequent calls to the same endpoint to obtain additional results. An API consumer
can use the `hasNextPage` and `hasPreviousPage` values to determine if there is more data in the dataset logically
before or after the result that was returned.


## WMS Data Upload

Ware supports uploading either a file or individual records sourced from a WMS system as a data source for comparisons
against detected state. This data upload process has 3 steps that are illustrated in the `wms_file_upload_example.py`
and the `wms_record_upload_example.py` scripts:

1. Call the either the createWMSLocationHistoryUpload or createWMSLocationHistoryRecords endpoint to initiate the
upload process.  In the case of a file upload, this will create a signed URL that the client will use to transmit the
WMS data file. The request and the return response will follow the following format in either case:

**Request:**

```graphql
mutation CreateWMSLocationHistoryUpload($zoneId: String!, $fileFormat: WMSUploadFormat) {
                createWMSLocationHistoryUpload(zoneId: $zoneId) {
                    id
                    uploadFields
                    uploadUrl
                }
            }
```
- or -
```graphql
mutation CreateWMSLocationHistoryRecords($zoneId: String!, $records: [WMSLocationHistoryRecord]!) {
                createWMSLocationHistoryRecords(zoneId: $zoneId, records: $records) {
                    id
                    uploadFields
                    uploadUrl
                }
            }
```

**Response:**

```json
{
  "data": {
    "createWMSLocationHistoryUpload": {
      "id": "810c2b23-a1ea-41ef-b527-0ace8fe49466",
      "uploadUrl": "<URL TO PERFORM POST UPLOAD>",
      "uploadFields": "<JSON STRING OF FIELDS THAT MUST BE INCLUDED WITH THE UPLOAD POST>"
    }
  }
}
```

- or -

```json
{
  "data": {
    "createWMSLocationHistoryRecords": {
      "id": "810c2b23-a1ea-41ef-b527-0ace8fe49466"
    }
  }
}
```

In the case of `createWMSLocationHistoryRecords` the `uploadUrl` and `uploadFields` return values can be ignored, and
the control flow can proceed to step 3.  Internally the individual records are batched and processed asynchronously in
the same manner as a file-based WMS upload.


2. Perform a HTTP POST operation on the returned URL to transmit the WMS data file. The data file may be either CSV or
   MS Excel XLSX format as specified by the optional format parameter.  At minimum, the file most contain a column named
   "Location" that contains a warehouse bin location, and a column named "LPN" which
   contains LPN data for that location.  If multiple LPNs are present in a location each entry should be on a
   separate line.  If the LPN column for a Location is empty the behaviour is dictated by the setup for the warehouse
   zone.  Please contact your Ware representative for information regarding support for indicating the absence of LPN
   data for a given warehouse zone.
   The POST must be made against the returned "uploadUrl" value and the returned value for
   "uploadFields" must be included in the POST data or the upload will be rejected.


3. Once the upload is complete the Ware back end will process the file.  To retrieve status information about the upload
   process the client can either poll the Ware back end periodically for status information, or subscribe to status
   updates for that upload processing job.   Both scenarios are shown in the sample script, and details of both follow

**Polling (read) request:**
```graphql
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
```

**Subscription request:**
```graphql
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
```


**Response:**

```json
{
   "data": {
      "subscribeWMSLocationHistoryUploadStatusChange": {
         "created":"2021-02-21T03:41:37+00:00",
         "failedRecords":0,
         "id":"810c2b23-a1ea-41ef-b527-0ace8fe49466",
         "processedRecords":0,
         "skippedRecords":0,
         "status":"PROCESSING",
         "totalRecords":0,
         "updated":"2021-02-21T03:41:42+00:00",
         "userId":"a7de417c-e6a2-4f57-8fa5-705c9ecb24d0",
         "zoneId":"47881736-b5d5-4341-a3ca-9ef63c342db3"
      }
   }
}
```
The response is of type `WMSLocationHistoryUpload` regardless of the method used.  The upload processing is considered
complete once the `status` value is either "SUCCESS" or "FAILURE" and the included sample script shows how to gracefully
complete processing for both status checking methods.

## Drone required actions

### Clear/reset a required action
**Description:**
This mutation may be used to remove required actions. The UUID for the specific required action is
necessary.

**Request:**
```graphql
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
```

**Response:**
```json
{
  "data": {
    "setDroneRequiredAction": {
      "nests": [
        {
          "drone": {
            "id": "06b6c19b-bba5-4b27-a9ad-e04590ba95b5",
            "requiredActions": []
          }
        },
        {
          "drone": {
            "id": "ffa3deef-9432-408b-9a11-862142fcaf5e",
            "requiredActions": [
              {
                "id": "03fa37f9-946f-497d-b6f1-e8bccc73a3d2",
                "action": null,
                "shortName": "Wait for it",
                "description": "This is a test action to where the system will detect the correction"
              }
            ]
          }
        },
        {
          "drone": {
            "id": "b9035ee9-bd78-4335-a8b1-2ac6393c547d",
            "requiredActions": [
              {
                "id": "ed30ca51-9a76-48c9-a06b-5860253e53e9",
                "action": null,
                "shortName": "Wait for it",
                "description": "This is a test action to where the system will detect the correction"
              }
            ]
          }
        },
        {
          "drone": {
            "id": "0bf4a26b-1ac3-4734-b00b-ef7c37b6ed2c",
            "requiredActions": []
          }
        }
      ]
    }
  }
}
```

## Location Scan Orders
Location scan orders are requests for Ware robot systems to scan an arbitrary set of bin locations in a warehouse zone.

### createLocationScanOrder
**Description:**
This mutation requires a `zoneId` and list of valid bin names for that zone. It also accepts an arbitrary string via
`userTrackingToken` which will be associated with the location scan order which can be used in the `getLocationScanOrders` query
to target location scan orders designated with the same user tracking token. Ware does not use any information in the user
tracking token, it simply encodes it as binary data and looks for a full match when necessary.

**Request:**

```graphql
mutation CreateLocationScanOrder($zoneId: String!, $bins: [String!]!, $userTrackingToken: String) {
  createLocationScanOrder(zoneId: $zoneId, bins: $bins, userTrackingToken: $userTrackingToken) {
    id
    createdAt
    userTrackingToken
  }
}
```

**Response:**
The `createLocationScanOrder` endpoint will return a JSON string with the fields specified by the client which resembles the following:

```json
{
  "data": {
    "createLocationScanOrder": {
      "id": "b9035ee9-bd78-4335-a8b1-2ac6393c547d",
      "createdAt": "2021-01-01T14:32:10+00:00",
      "userTrackingToken": "customer-supplied tracking token 01"
    }
  }
}
```

### getLocationScanOrder
**Description:**
This query response provides information about the location scan order, its overall status, and the status of the scan for each bin that was
specified when the location scan order was created.

**Request:**

```graphql
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
```

**Response:**
The `getLocationScanOrder` endpoint will return a JSON string with the fields specified by the client which resembles the following:

```json
{
  "data": {
    "getLocationScanOrder": {
        {
          "id": "00000000-beef-beef-beef-000000000000",
          "zoneId": "00000000-cafe-0000-0000-000000000005",
          "userTrackingToken": null,
          "status": "SUCCEEDED",
          "createdAt": "2021-01-01T00:00:00+00:00",
          "startTime": "2021-01-01T00:15:00+00:00",
          "endTime": null,
          "bins": [
            {
              "id": "00000000-cafe-cafe-face-000000000001",
              "status": "SUCCEEDED",
              "record": {
                "recordId": "00000000-dead-cafe-face-000000000001",
                "aisle": "XYZ",
                "binName": "XYZ-103-A-1",
                "timestamp": "2021-01-01T01:00:00+00:00",
                "inventory": [
                  {
                    "lpn": "LPN00001",
                    "recordId": "00000000-face-face-face-000000000001"
                  },
                  {
                    "lpn": "LPN00002",
                    "recordId": "00000000-face-face-face-000000000002"
                  }
                ],
                "exceptions": [],
                "userStatus": null,
                "sharedLocationViewUrl": "FAKEBASEURL/00000000deadcafeface000000000001/view?token=000000"
              },
              "errors": []
            },
            {
              "id": "00000000-cafe-cafe-face-000000000002",
              "status": "SUCCEEDED",
              "record": {
                "recordId": "00000000-dead-cafe-face-000000000002",
                "aisle": "XYZ",
                "binName": "XYZ-103-A-2",
                "timestamp": "2021-01-01T01:00:00+00:00",
                "inventory": [
                  {
                    "lpn": "LPN00003",
                    "recordId": "00000000-face-face-face-000000000003"
                  },
                  {
                    "lpn": "LPN00004",
                    "recordId": "00000000-face-face-face-000000000004"
                  }
                ],
                "exceptions": [],
                "userStatus": null,
                "sharedLocationViewUrl": "FAKEBASEURL/00000000deadcafeface000000000002/view?token=000000"
              },
              "errors": []
            },
            {
              "id": "00000000-cafe-cafe-face-000000000003",
              "status": "SUCCEEDED",
              "record": {
                "recordId": "00000000-dead-cafe-face-000000000003",
                "aisle": "XYZ",
                "binName": "XYZ-103-B-1",
                "timestamp": "2021-01-01T01:00:00+00:00",
                "inventory": [
                  {
                    "lpn": "LPN00005",
                    "recordId": "00000000-face-face-face-000000000005"
                  },
                  {
                    "lpn": "LPN00006",
                    "recordId": "00000000-face-face-face-000000000006"
                  }
                ],
                "exceptions": [],
                "userStatus": null,
                "sharedLocationViewUrl": "FAKEBASEURL/00000000deadcafeface000000000003/view?token=000000"
              },
              "errors": []
            },
            {
              "id": "00000000-cafe-cafe-face-000000000004",
              "status": "SUCCEEDED",
              "record": {
                "recordId": "00000000-dead-cafe-face-000000000004",
                "aisle": "XYZ",
                "binName": "XYZ-103-B-2",
                "timestamp": "2021-01-01T01:00:00+00:00",
                "inventory": [
                  {
                    "lpn": "LPN00006",
                    "recordId": "00000000-face-face-face-000000000007"
                  }
                ],
                "exceptions": [],
                "userStatus": null,
                "sharedLocationViewUrl": "FAKEBASEURL/00000000deadcafeface000000000004/view?token=000000"
              },
              "errors": []
            }
          ]
        }
      }
    }
  }
}
```

### getLocationScanOrders
**Description:**
This query response provides information about a collection of location scan orders for a zone, optionally filtered
by user tracking token or status.

**Request:**

```graphql
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
```

**Response:**

```json
{
  "data": {
    "getLocationScanOrder": {
      "zoneId": "00000000-cafe-0000-0000-000000000005",
      "status": null,
      "userTrackingToken": null,
      "orders": [
        {
          "id": "00000000-beef-beef-beef-000000000000",
          "zoneId": "00000000-cafe-0000-0000-000000000005",
          "userTrackingToken": "a silly string",
          "status": "SUCCEEDED",
          "createdAt": "2021-01-01T00:00:00+00:00",
          "startTime": "2021-01-01T00:15:00+00:00",
          "endTime": "2021-01-01T01:00:00+00:00",
          "bins": [
            {
              "id": "00000000-cafe-cafe-face-000000000001",
              "status": "SUCCEEDED",
              "record": {
                "recordId": "00000000-dead-cafe-face-000000000001",
                "aisle": "XYZ",
                "binName": "XYZ-103-A-1",
                "timestamp": "2021-01-01T01:00:00+00:00",
                "inventory": [
                  {
                    "lpn": "LPN00001",
                    "recordId": "00000000-face-face-face-000000000001"
                  },
                  {
                    "lpn": "LPN00002",
                    "recordId": "00000000-face-face-face-000000000002"
                  }
                ],
                "exceptions": [],
                "userStatus": null,
                "sharedLocationViewUrl": "FAKEBASEURL/00000000deadcafeface000000000001/view?token=000000"
              },
              "errors": []
            },
            {
              "id": "00000000-cafe-cafe-face-000000000002",
              "status": "SUCCEEDED",
              "record": {
                "recordId": "00000000-dead-cafe-face-000000000002",
                "aisle": "XYZ",
                "binName": "XYZ-103-A-2",
                "timestamp": "2021-01-01T01:00:00+00:00",
                "inventory": [
                  {
                    "lpn": "LPN00003",
                    "recordId": "00000000-face-face-face-000000000003"
                  },
                  {
                    "lpn": "LPN00004",
                    "recordId": "00000000-face-face-face-000000000004"
                  }
                ],
                "exceptions": [],
                "userStatus": null,
                "sharedLocationViewUrl": "FAKEBASEURL/00000000deadcafeface000000000002/view?token=000000"
              },
              "errors": []
            }
          ]
        },
        {
          "id": "00000000-beef-beef-beef-000000000001",
          "zoneId": "00000000-cafe-0000-0000-000000000005",
          "userTrackingToken": "a silly string",
          "status": "IN_PROGRESS",
          "createdAt": "2021-01-01T00:00:00+00:00",
          "startTime": "2021-01-01T00:15:00+00:00",
          "endTime": null,
          "bins": [
            {
              "id": "00000000-cafe-cafe-face-000000000003",
              "status": "IN_PROGRESS",
              "record": null,
              "errors": []
            },
            {
              "id": "00000000-cafe-cafe-face-000000000004",
              "status": "IN_PROGRESS",
              "record": null,
              "errors": []
            }
          ]
        }
      ]
    }
  }
}
```
