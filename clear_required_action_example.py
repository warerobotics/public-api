import json
import argparse
from ware_api import WareAPI, DEFAULT_HOST

SUCCESS_STATUS = 'success'


def main() -> None:
    parser = argparse.ArgumentParser(
        description="""
    # Clear drone required actions via the Ware GraphQL API
    # To use this tool you must define 2 environment variables (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY).
    # You can get these values from your Ware service representative.
    # """
    )

    parser.add_argument('--required-action-id', help='The required action id to clear', required=True)
    parser.add_argument(
        "--endpoint", type=str, help="Optional endpoint value to override the default", default=DEFAULT_HOST
    )

    args = parser.parse_args()

    api = WareAPI(host=args.endpoint)

    result = api.reset_required_action(args.required_action_id)

    if result['status'] != SUCCESS_STATUS:
        return result

    print(f'Required action {args.required_action_id} cleared')

if __name__ == '__main__':
    result = main()
    if result:
        print(json.dumps(result, indent=2))
