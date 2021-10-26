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

## Queries

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

### zoneLocationsPage

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
            "userStatus": null
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

Ware supports uploading a file sourced from a WMS system as a data source for comparisons against detected state. This
data upload process has 3 steps that are illustrated in the `wms_upload.py` script:

1. Call the createWMSLocationHistoryUpload endpoint to initiate the upload process.  This will create a signed URL that
the client will use to transmit the WMS data file. The request and the return respose will follow the following format:

**Request:**

```graphql
mutation CreateWMSLocationHistoryUpload($zoneId: String!) {
                createWMSLocationHistoryUpload(zoneId: $zoneId) {
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
   
2. Perform a HTTP POST operation on the returned URL to transmit the WMS data file. The data file must be a CSV file 
   with, at minimum, a column named "Location" that contains a warehouse bin location, and a column named "LPN" which 
   contains LPN data for that location.  If multiple LPNs are present in a location each entry should be on a 
   separate line.  The POST must be made against the returned "uploadUrl" value and the returned value for 
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
