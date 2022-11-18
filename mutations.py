create_wms_location_history_upload = """
    mutation CreateWMSUpload($zoneId: String!, $format: WMSUploadFormat) {
      createWMSLocationHistoryUpload(zoneId: $zoneId, format: $format) {
        id
        uploadFields
        uploadUrl
      }
    }
"""

create_wms_location_history_records = """
    mutation CreateWMSLocationHistoryRecords($zoneId: String!, $records: [WMSLocationHistoryRecord]!) {
        createWMSLocationHistoryRecords(zoneId: $zoneId, records: $records) {
            id
            uploadFields
            uploadUrl
        }
    }
"""

reset_drone_required_action = """
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

create_location_scan_order = """
    mutation CreateLocationScanOrder($zoneId: String!, $bins: [String!]!, $userTrackingToken: String) {
      createLocationScanOrder(zoneId: $zoneId, bins: $bins, userTrackingToken: $userTrackingToken) {
        id
        createdAt
        userTrackingToken
      }
    }
"""
