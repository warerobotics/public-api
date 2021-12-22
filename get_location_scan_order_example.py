import uuid
import json
import argparse
from ware_api import WareAPI, DEFAULT_HOST


def main() -> None:
    parser = argparse.ArgumentParser(
        description="""
    # Interact with the Ware GraphQL API
    # To use this tool you must define 2 environment variables (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY).
    # You can get these values from your Ware service representative.
    # """
    )

    parser.add_argument(
        "--endpoint", type=str, help="Optional endpoint value to override the default", default=DEFAULT_HOST
    )
    parser.add_argument("id", help="LocationScanOrder UUID")

    args = parser.parse_args()

    try:
        lso_id = uuid.UUID(f'urn:uuid:{args.id}')
    except TypeError:
        print(f'Invalid id: {args.id}')
        exit(1)

    api = WareAPI(host=args.endpoint)

    response = api.get_location_scan_order(str(lso_id))

    print(json.dumps(response, indent=2))


if __name__ == '__main__':
    main()
