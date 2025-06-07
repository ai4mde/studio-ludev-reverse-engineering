from ninja import Schema

class ExtractJinjaRequest(Schema):
    extract_path: str
    project_id: str
    system_id: str
    include_method_dependencies: bool

class ExtractJinjaResponse(Schema):
    success: bool
    header: str
    message: str
    diagram_json: str = ""

class ZipUploadResponse(Schema):
    success: bool
    message: str
    extract_path: str


__all__ = ["ExtractJinjaRequest", "ExtractJinjaResponse", "ZipUploadResponse"]
