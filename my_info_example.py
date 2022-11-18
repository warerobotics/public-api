#!/usr/bin/env python
import argparse
import json
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
    args = parser.parse_args()

    api = WareAPI(host=args.endpoint)
    # Use JSON format string for the query. It does not need reformatting.

    my_info_result = api.my_info()

    if my_info_result["status"] != "success":
        print(f"Error calling myInfo: {my_info_result['message']}.\n"
              "Ensure proper AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set and "
              "configured properly in the Ware portal")
        return

    # Print the output to the console.
    print(json.dumps(my_info_result["data"], indent=2))


if __name__ == "__main__":
    main()
