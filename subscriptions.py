wms_location_history_upload_status_change = """
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

location_scan_orders = """
    subscription SubscribeLocationScanOrders($zoneId: String!) {
      subscribeLocationScanOrders(zoneId: $zoneId) {
        zoneId
        userTrackingToken
        status
        orders {
          id
          zoneId
          status
          createdAt
          startTime
          endTime
          userTrackingToken
          bins {
            id
            status
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
              inventory {
                lpn
                recordId
              }
              recordId
              sharedLocationViewUrl
              timestamp
              userStatus
            }
          }
        }
      }
    }
"""
