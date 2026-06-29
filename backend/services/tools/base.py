class BaseTool:
    name: str
    description: str

    def get_schema(self) -> dict:
        raise NotImplementedError

    def validate_params(self, params: dict) -> dict:
        return {"valid": True, "error": None}

    def execute(self, **kwargs) -> str:
        raise NotImplementedError
