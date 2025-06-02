import subprocess
from diagram.api import diagram_router
from django.http import HttpResponse
import zipfile
from datetime import datetime
from pathlib import Path
from metadata.api import metadata_router
from prose.api import prose_router
from generator.api import generator_router
from ninja import NinjaAPI, Schema
from ninja.files import UploadedFile

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
def upload_zip(request, file: UploadedFile = None, is_zip: str = None):
    try:
        # 打印调试信息
        print(f"Upload request received: is_zip={is_zip}")
        print(f"FILES in request: {list(request.FILES.keys())}")
        
        # make sure uploadpath existed
        UPLOAD_DIR = Path("/usr/src/uploads")
        UPLOAD_DIR.mkdir(exist_ok=True)
        
        # Create a timestamped subfolder to differentiate between multiple uploads
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extract_dir = UPLOAD_DIR / f"extract_{timestamp}"
        extract_dir.mkdir(exist_ok=True)
        
        # 严格判断是否是文件夹上传 - 检查is_zip参数和FILES中是否包含files[]
        folder_upload = False
        folder_files = []
        
        for key in request.FILES.keys():
            if key.startswith('files'):
                folder_files.extend(request.FILES.getlist(key))
                folder_upload = True
                
        # 如果有files开头的键或is_zip明确设置为false，则认为是文件夹上传
        if folder_upload or (is_zip and is_zip.lower() == 'false'):
            print("Handling folder upload...")
            print(f"Found {len(folder_files)} files in folder upload")
            
            if not folder_files:
                print("No files found in folder upload")
                return {
                    "success": False,
                    "message": "No files received for folder upload"
                }
            
            # Process each file maintaining the relative path structure
            file_count = 0
            for uploaded_file in folder_files:
                try:
                    # Get the relative path from the filename
                    rel_path = uploaded_file.name
                    print(f"Processing file: {rel_path}")
                    
                    # Create the destination path
                    dest_path = extract_dir / rel_path
                    # Ensure the directory exists
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    # Write the file
                    with open(dest_path, 'wb') as dest:
                        dest.write(uploaded_file.read())
                    file_count += 1
                except Exception as e:
                    print(f"Error processing file {uploaded_file.name}: {str(e)}")
            
            print(f"Successfully processed {file_count} files")
            return {
                "success": True,
                "message": f"Folder with {file_count} files uploaded successfully",
                "extract_path": str(extract_dir)
            }
        else:
            # ZIP文件上传处理
            print("Handling ZIP file upload...")
            # 验证file是否存在
            if not file:
                print("No file provided for ZIP upload")
                return {
                    "success": False,
                    "message": "No ZIP file received"
                }
            
            # 输出文件信息
            print(f"ZIP File received: {file.name}, size: {file.size} bytes")
            
            # save file
            zip_path = UPLOAD_DIR / f"{timestamp}_{file.name}"
            with open(zip_path, "wb") as f:
                f.write(file.read())
            
            # unzip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            print(f"ZIP file extracted to: {extract_dir}")
            return {
                "success": True,
                "message": f"Zip file {file.name} uploaded and extracted successfully",
                "extract_path": str(extract_dir)
            }
        
    except Exception as e:
        import traceback
        print(f"Error processing upload: {str(e)}")
        print(traceback.format_exc())
        return {
            "success": False,
            "message": f"Error processing upload: {str(e)}"
        }

class ExtractJinjaRequest(Schema):
    extract_path: str
    project_id: str
    system_id: str
    include_method_dependencies: bool


class ExtractJinjaResponse(Schema):
    success: bool
    message: str
    diagram_json: str = None


@api.post("/utils/extract-jinja", response=ExtractJinjaResponse, tags=["utils"])
def extract_jinja(request, data: ExtractJinjaRequest):
    try:
        extract_path = data.extract_path
        project_id = data.project_id
        system_id = data.system_id
        is_method_dependencies = data.include_method_dependencies
        
        # Open subprocess with extraction
        p1 = subprocess.Popen([
            "python3", 
            "/usr/src/model/model/utils/extract_relationships.py", 
            "-p", extract_path, 
            "-pid", project_id, 
            "-sid", system_id,
            "-md", str(is_method_dependencies)
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        diagram_json, error = p1.communicate()
        # Generate the diagram JSON

        return {
            "success": True,
            "message": "Jinja template extracted successfully",
            "diagram_json": diagram_json
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error extracting Jinja template: {str(e)}"
        }
