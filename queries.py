my_info = """
    query MyInfo {
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

get_zone_locations = """
    query ZoneLocationsPageV2(
      $zoneId: String!,
      $limit: Int,
      $cursor: String,
      $paginate: Pagination,
      $filter: LocationFilterV2,
      $sort: RecordSort,
      $includeImages: Boolean = false,
      $includeInventory: Boolean = true
    ) {
      zoneLocationsPageV2(
        zoneId: $zoneId,
        limit: $limit,
        cursor: $cursor,
        paginate: $paginate,
        filter: $filter,
        sort: $sort
    ) {
        pageInfo {
          endCursor
          hasNextPage
          hasPrevPage
          startCursor
          startIndex
          totalRecords
        }
        timezone
        zoneId
        records {
          record {
            id
            aisle
            binName
            timestamp
            sharedLocationViewUrl
            exceptions {
              id
              type
              exceptionHistory {
                timestamp
                comments
                userId
                userStatus
              }
              parameters {
                lpn
                sku
                binLocation
                binLocations
                lpnPresentInWms
                skuPresentInWms
                locationPresentInWms
                wmsReportedLpns
                wmsReportedBinLocation
              }
            }
            images @include(if: $includeImages) {
              large
              binLocationOverlay {
                label
                polygon {
                  x
                  y
                }
              }
              detectionOverlays {
                label
                polygon {
                  x
                  y
                }
              }
              original
              thumbnail
            }
            inventory @include(if: $includeInventory) {
              id
              type
              text
              exceptions {
                id
                type
                exceptionHistory {
                  comments
                  timestamp
                  userId
                  userStatus
                }
                parameters {
                  lpn
                  sku
                  binLocation
                  binLocations
                  lpnPresentInWms
                  skuPresentInWms
                  locationPresentInWms
                  wmsReportedLpns
                  wmsReportedBinLocation
                }
              }
              images @include(if: $includeImages) {
                binLocationOverlay {
                  label
                  polygon {
                    x
                    y
                  }
                }
                large
                detectionOverlays {
                  label
                  polygon {
                    x
                    y
                  }
                }
                original
                thumbnail
              }
            }
            wmsRecords {
              lpn
              sku
              updatedAt
              wmsData
            }
          }
          cursor
        }
      }
    }
"""

get_zone_locations_report = """
    query GetZoneLocationsReport($zoneId: String!, $filter: LocationFilterV2, $sort: RecordSort, $reportFormat: SpreadsheetFormat) {
      zoneLocationsReport(
        zoneId: $zoneId
        filter: $filter
        sort: $sort
        reportFormat: $reportFormat
      ) {
        zoneInventoryReportUrl
      }
    }
"""

get_location_scan_order = """
    query GetLocationScanOrder($id: String!, $includeBins: Boolean = true, $includeSummary: Boolean = true, $includeImages: Boolean = false) {
      getLocationScanOrder(id: $id) {
        id
        status
        zoneId
        createdAt
        startTime
        endTime
        userTrackingToken
        summary @include(if: $includeSummary) {
          totalBins
          queuedBinCount
          queuedBinNames
          inProgressBinCount
          inProgressBinNames
          succeededBinCount
          succeededBinNames
          errorBinCount
          errorBinNames
          canceledBinCount
          canceledBinNames
        }
        bins @include(if: $includeBins) {
          id
          error {
            id
            message
            timestamp
            type
          }
          record {
            aisle
            binName
            exceptions {
              description
              type
            }
            images @include(if: $includeImages) {
              large
              binLocationOverlay {
                label
                polygon {
                  x
                  y
                }
              }
              lpnOverlays {
                label
                polygon {
                  x
                  y
                }
              }
              original
              thumbnail
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
      }
    }
"""

get_location_scan_orders = """
    query GetLocationScanOrders(
      $zoneId: String!,
      $userTrackingToken: String,
      $status: [LocationScanOrderStatus!],
      $includeOrders: Boolean = true,
      $includeSummary: Boolean = true,
      $includeBins: Boolean = false,
      $includeImages: Boolean = false
    ) {
      getLocationScanOrders(zoneId: $zoneId, userTrackingToken: $userTrackingToken, status: $status) {
        status
        userTrackingToken
        zoneId
        orders @include(if: $includeOrders) {
          createdAt
          id
          name
          endTime
          startTime
          status
          userTrackingToken
          zoneId
          summary @include(if: $includeSummary) {
            totalBins
            queuedBinCount
            queuedBinNames
            inProgressBinCount
            inProgressBinNames
            succeededBinCount
            succeededBinNames
            errorBinCount
            errorBinNames
            canceledBinCount
            canceledBinNames
          }
          bins @include(if: $includeBins) {
            id
            status
            error {
              id
              message
              timestamp
              type
            }
            record {
              recordId
              timestamp
              userStatus
              aisle
              binName
              sharedLocationViewUrl
              exceptions {
                type
                description
              }
              images @include(if: $includeImages) {
                large
                original
                thumbnail
                binLocationOverlay {
                  label
                  polygon {
                    x
                    y
                  }
                }
                detectionOverlays {
                  label
                  polygon {
                    x
                    y
                  }
                }
              }
              inventory {
                lpn
                recordId
              }
            }
          }
        }
      }
    }
"""

get_wms_location_history_upload_record = """
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
