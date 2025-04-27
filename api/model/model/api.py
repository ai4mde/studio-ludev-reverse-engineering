from diagram.api import diagram_router
from django.http import HttpResponse
from metadata.api import metadata_router
from prose.api import prose_router
from generator.api import generator_router
from ninja import NinjaAPI, Schema

from model.auth import auth, create_token

api = NinjaAPI(
    title="AI4MDE Studio",
    version="0.0.1",  # TODO: Use package-wide versioning
    description="AI4MDE Studio API",
    auth=auth,
    csrf=False,  # TODO: Ensure this works with Axios frontend / XSRF Header
)
api.add_router("/metadata/", metadata_router)
api.add_router("/diagram/", diagram_router)
api.add_router("/prose/", prose_router)
api.add_router("/generator/", generator_router)


class GetTokenSchema(Schema):
    username: str
    password: str


@api.post("/auth/token", auth=None, tags=["authentication"])
def get_token(request, body: GetTokenSchema, response: HttpResponse):
    user, token = create_token(body.username, body.password)
    if user and token:
        response.set_cookie(
            "key",
            token,
            httponly=True,
        )
        return {
            "token": token,
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }
    return 403, {"message": "User not found."}


@api.post("/auth/logout", tags=["authentication"])
def logout(request, response: HttpResponse):
    response.delete_cookie("key")
    return {"message": "Logged out."}


@api.get("/auth/status", tags=["authentication"])
def get_auth(request):
    if user := request.auth:
        return 200, {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }
    return 403, {"id": None}


class ZipUploadResponse(Schema):
    success: bool
    message: str
    extract_path: str = None


@api.post("/utils/upload-zip", response=ZipUploadResponse, tags=["utils"])
def upload_zip(request, file: UploadedFile = File(...)):
    try:
        # 确保上传目录存在
        UPLOAD_DIR = Path("/usr/src/uploads")
        UPLOAD_DIR.mkdir(exist_ok=True)
        
        # 创建一个时间戳子文件夹以区分多次上传
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extract_dir = UPLOAD_DIR / f"extract_{timestamp}"
        extract_dir.mkdir(exist_ok=True)
        
        # 保存上传的文件
        zip_path = UPLOAD_DIR / f"{timestamp}_{file.name}"
        with open(zip_path, "wb") as f:
            f.write(file.read())
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # 返回成功信息和解压位置
        return {
            "success": True,
            "message": f"File {file.name} uploaded and extracted successfully",
            "extract_path": str(extract_dir)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing ZIP file: {str(e)}"
        }

