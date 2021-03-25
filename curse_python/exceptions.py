class RequestException(Exception):
    def __init__(self, status_code, message="Request error"):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

class CanNotResolveException(Exception):
    def __init__(self, addon_id, version_targets):
        self.addon_id = addon_id
        self.message = f'Addon ID {addon_id} is not compatiable with versions {version_targets}'
        super().__init__(self.message)