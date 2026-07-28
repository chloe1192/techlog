# techlog/api.py

import requests


class TechlogClient:
    """
    Client for the Techlog Django app's API,
    running as a separate service.
    """

    BASE_URL = "http://127.0.0.1:8001/api/v1"

    def __init__(self, auth_token: str | None = None):
        self.session = requests.Session()

        # Placeholder for future auth
        if auth_token:
            self.session.headers.update({
                "Authorization": f"Token {auth_token}"
            })

    def _request(self, method, endpoint, params=None, data=None, json_data=None):
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self.session.request(
                method,
                url,
                params=params,
                data=data,
                json=json_data,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"Techlog API returned {response.status_code}: {response.text}"
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Could not connect to Techlog API at {url}") from e
        except requests.exceptions.Timeout as e:
            raise RuntimeError("Request to Techlog API timed out.") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}") from e
        except ValueError as e:
            raise RuntimeError("Techlog API returned invalid JSON.") from e

    def get(self, endpoint, params=None):
        print(f"{self.BASE_URL}/{endpoint}")
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data=None, json_data=None):
        return self._request("POST", endpoint, data=data, json_data=json_data)

    def put(self, endpoint, data=None, json_data=None):
        return self._request("PUT", endpoint, data=data, json_data=json_data)
    
    def delete(self, endpoint, params=None):
        return self._request("DELETE", endpoint, params=params)