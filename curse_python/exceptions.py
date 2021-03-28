class RequestException(Exception):
    def __init__(self, status_code, message="Request error"):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

class CanNotResolveException(Exception):
    def __init__(self, project_id, version_targets):
        self.project_id = project_id
        self.message = f'Project ID {project_id} is not compatible with versions {version_targets}'
        super().__init__(self.message)