from .exceptions import HunterApiError


def parse_data_payload(response, endpoint, method):
    try:
        return response.json()["data"]
    except (KeyError, ValueError) as exc:
        try:
            payload_data = response.json()
        except ValueError:
            payload_data = {"body": response.text}
        raise HunterApiError(
            message="Hunter API response format is invalid",
            status_code=response.status_code,
            payload=payload_data,
            endpoint=endpoint,
            method=method,
        ) from exc
