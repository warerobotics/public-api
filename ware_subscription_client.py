import hashlib
import hmac

from base64 import b64encode
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, Callable

import boto3
import websocket
import threading
import json

AWS_SERVICE = "appsync"
DEFAULT_REGION = "us-east-1"
SUBSCRIPTION_ID = str(uuid4())  # Client generated subscription ID

# Set up Timeout Globals
timeout_timer: threading.Timer = None
timeout_interval = 10
graphql_subscription: Dict = {}
sts_credentials: Dict = {}
host: str = ""
data_handler_function: Callable
websocket_app: websocket.WebSocketApp


def _get_signature_key(key, date_stamp, region_name, service_name):
    # Key derivation functions. See:
    # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(sig_key, msg):
        return hmac.new(sig_key, msg.encode("utf-8"), hashlib.sha256).digest()

    k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, "aws4_request")
    return k_signing


def _canonical_headers(headers: Dict[str, Any]) -> str:
    """
    Create the canonical headers. Header names must be trimmed
    and lowercase, and sorted in code point order from low to high.
    Note that there is a trailing \n.
    """
    canonical_headers = ""
    for header_name, v in headers.items():
        canonical_headers += f"{header_name}:{v}\n"
    return canonical_headers


def _generate_authorization_header(
    security_token: str,
    aws_access_key: str,
    aws_secret_key: str,
    canonical_uri: str,
    method: str,
    request_parameters: str,
) -> str:
    # Create a date for headers and the credential string
    global host

    t = datetime.utcnow()
    amz_date = t.strftime("%Y-%m-%dT%H:%M:%SZ")
    header_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")  # Date w/o time, used in credential scope

    # Create the canonical query string. Request parameters are passed in the body of the request
    # and the query string is blank.
    canonical_querystring = ""

    headers = {
        "accept": "application/json, text/javascript",
        "content-encoding": "amz-1.0",
        "content-length": len(request_parameters),
        "content-type": "application/json; charset=UTF-8",
        "host": host,
        "x-amz-date": amz_date,
        "x-amz-security-token": security_token,
    }
    canonical_headers = _canonical_headers(headers)
    signed_headers = ";".join(headers.keys())

    # Combine elements to create canonical request
    canonical_request = "\n".join(
        [
            method,
            canonical_uri,
            canonical_querystring,
            canonical_headers,
            signed_headers,
            hashlib.sha256(request_parameters.encode("utf-8")).hexdigest(),  # Payload Hash
        ]
    )

    # Match the algorithm to the hashing algorithm you use, either SHA-1 or SHA-256 (recommended)
    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = date_stamp + "/" + DEFAULT_REGION + "/" + AWS_SERVICE + "/" + "aws4_request"
    string_to_sign = (
        algorithm
        + "\n"
        + header_date
        + "\n"
        + credential_scope
        + "\n"
        + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    )

    # Create the signing key using the function defined above.
    signing_key = _get_signature_key(aws_secret_key, date_stamp, DEFAULT_REGION, AWS_SERVICE)

    # Sign the string_to_sign using the signing_key
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    header = (
        f"{algorithm} Credential={aws_access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    return header


def _generate_iam_header(
    canonical_uri: str,
    request_parameters: str,
    security_token: str,
    aws_access_key: str,
    aws_secret_key: str,
) -> Dict:
    # Create the AWS IAM header for request signing
    global host
    iam_signature = _generate_authorization_header(
        security_token=security_token,
        aws_access_key=aws_access_key,
        aws_secret_key=aws_secret_key,
        canonical_uri=canonical_uri,
        method="POST",
        request_parameters=request_parameters,
    )
    aws_header = {
        "accept": "application/json, text/javascript",
        "content-encoding": "amz-1.0",
        "content-length": "2",
        "content-type": "application/json; charset=UTF-8",
        "host": host,
        "x-amz-date": _header_time(),
        "x-amz-security-token": security_token,
        "Authorization": iam_signature,
    }
    return aws_header


def _header_time() -> str:
    # Calculate UTC time in ISO format (AWS Friendly): YYYY-MM-DDTHH:mm:ssZ
    return datetime.utcnow().isoformat(sep="T", timespec="seconds") + "Z"


def _header_encode(header_obj: Dict) -> str:
    # Encode Using Base 64
    return b64encode(json.dumps(header_obj).encode("utf-8")).decode("utf-8")


def reset_timer(ws: websocket.WebSocket) -> None:
    # reset the keep alive timeout daemon thread
    global timeout_timer
    global timeout_interval

    if timeout_timer:
        timeout_timer.cancel()

    timeout_timer = threading.Timer(timeout_interval, lambda: ws.close())
    timeout_timer.daemon = True
    timeout_timer.start()


def on_message(ws: websocket.WebSocket, message: str) -> None:
    # Socket Event Callbacks, used in WebSocketApp Constructor
    global timeout_timer
    global timeout_interval
    global graphql_subscription
    global sts_credentials
    global host
    global data_handler_function

    print("### message ###")
    print("<< " + message)

    message_object = json.loads(message)
    message_type = message_object["type"]

    if message_type == "ka":
        reset_timer(ws)

    elif message_type == "connection_ack":
        timeout_interval = int(json.dumps(message_object["payload"]["connectionTimeoutMs"]))

        iam_header = _generate_iam_header(
            canonical_uri="/graphql",
            request_parameters=json.dumps(graphql_subscription),
            security_token=sts_credentials["Credentials"]["SessionToken"],
            aws_access_key=sts_credentials["Credentials"]["AccessKeyId"],
            aws_secret_key=sts_credentials["Credentials"]["SecretAccessKey"],
        )
        register = {
            "id": SUBSCRIPTION_ID,
            "type": "start",
            "payload": {
                "data": json.dumps(graphql_subscription),
                "extensions": {"authorization": iam_header},
            },
        }
        start_sub = json.dumps(register)
        print(">> " + start_sub)
        ws.send(start_sub)

    elif message_type == "data":
        data_handler_function(ws, message)

    elif message_object["type"] == "error":
        print("Error from AppSync: " + message_object["payload"])


def on_error(ws: websocket.WebSocket, error: str) -> None:
    print("### error ###")
    print(error)


def on_close(ws: websocket.WebSocket) -> None:
    print("### closed ###")


def on_open(ws: websocket.WebSocket) -> None:
    print("### opened ###")
    init = {"type": "connection_init"}
    init_conn = json.dumps(init)
    print(">> " + init_conn)
    ws.send(init_conn)


def subscribe(
    aws_access_key: str,
    aws_secret_key: str,
    api_url: str,
    subscription: str,
    subscription_variables: Dict,
    data_handler: Callable,
) -> None:

    global graphql_subscription
    global sts_credentials
    global host
    global data_handler_function
    global websocket_app

    # Derived values from the AppSync endpoint (api_url)
    wss_url = api_url.replace("https", "wss").replace("appsync-api", "appsync-realtime-api")
    host = api_url.replace("https://", "").replace("/graphql", "")
    data_handler_function = data_handler

    # Use Boto to get our security token from AWS STS
    sts = boto3.client("sts", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    sts_credentials = sts.get_session_token()

    # GraphQL subscription Registration object
    graphql_subscription = {"query": subscription, "variables": subscription_variables}
    iam_header = _generate_iam_header(
        canonical_uri="/graphql/connect",
        request_parameters="{}",
        security_token=sts_credentials["Credentials"]["SessionToken"],
        aws_access_key=sts_credentials["Credentials"]["AccessKeyId"],
        aws_secret_key=sts_credentials["Credentials"]["SecretAccessKey"],
    )
    # Uncomment to see socket byte streams
    # websocket.enableTrace(True)

    # Set up the connection URL, which includes the Authentication Header
    #   and a payload of '{}'.  All info is base 64 encoded
    connection_url = wss_url + "?header=" + _header_encode(iam_header) + "&payload=e30="

    # Create the websocket connection to AppSync's real-time endpoint
    #  also defines callback functions for websocket events
    #  NOTE: The connection requires a sub protocol 'graphql-ws'
    print("Connecting to: " + connection_url)

    websocket_app = websocket.WebSocketApp(
        connection_url,
        subprotocols=["graphql-ws"],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    websocket_app.run_forever()


def unsubscribe(subscription_id: str, web_socket: websocket.WebSocket) -> None:
    global websocket_app

    # Send the close messaging through the websocket
    deregister = {"type": "stop", "id": subscription_id}
    end_sub = json.dumps(deregister)
    print(">> " + end_sub)
    web_socket.send(end_sub)

    websocket_app.close()
    websocket_app.keep_running = False
