import subprocess
import sys
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
        res = subprocess.Popen([
            "python3", 
            "/usr/src/model/model/utils/extract_relationships.py", 
            "-p", extract_path, 
            "-pid", project_id, 
            "-sid", system_id,
            "-md", str(is_method_dependencies)
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        output = res.communicate()
        if res.returncode == 0:
            return {
                "success": True,
                "message": "Jinja template extracted successfully",
                "diagram_json": output
            }
        else:
            decoded_error = output[0].decode(sys.stdout.encoding)
            print(f"Error: {decoded_error}")
            return {
                "success": False,
                "message": f"Error extracting Jinja template: {str(decoded_error)}"
            }
    except OSError as e:
        return {
            "success": False,
            "message": f"Error extracting Jinja template: {str(e)}"
        }


class ExecuteImportDiagramRequest(Schema):
    include_method_dependency: bool = True


class ExecuteImportDiagramResponse(Schema):
    success: bool
    message: str


@api.post("/utils/execute-import-diagram", response=ExecuteImportDiagramResponse, tags=["utils"])
def execute_import_diagram(request, data: ExecuteImportDiagramRequest):
    try:
        include_method_dependency = data.include_method_dependency
        
        # Try the simplified script first for testing
        cmd = ["python3", "/usr/src/scripts/src/import_diagram_simple.py"]
        if include_method_dependency:
            cmd.append("--include-method-dependency")
        else:
            cmd.append("--no-method-dependency")
        
        print(f"Executing command: {' '.join(cmd)}")
        
        # Execute the import diagram script
        p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="/usr/src/scripts/src")
        
        output, error = p1.communicate()
        output_text = output.decode() if output else ""
        
        print(f"Script output: {output_text}")
        print(f"Return code: {p1.returncode}")
        
        # Check if the process was successful
        if p1.returncode == 0:
            return {
                "success": True,
                "message": f"Import diagram executed successfully with method dependency: {include_method_dependency}. Output: {output_text[-100:]}"
            }
        else:
            # If simplified script fails, try the original one
            cmd_original = ["python3", "/usr/src/scripts/src/import_diagram.py"]
            if include_method_dependency:
                cmd_original.append("--include-method-dependency")
            else:
                cmd_original.append("--no-method-dependency")
            
            print(f"Simplified script failed, trying original: {' '.join(cmd_original)}")
            
            p2 = subprocess.Popen(cmd_original, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="/usr/src/scripts/src")
            output2, error2 = p2.communicate()
            output_text2 = output2.decode() if output2 else ""
            
            if p2.returncode == 0:
                return {
                    "success": True,
                    "message": f"Import diagram executed successfully with original script. Method dependency: {include_method_dependency}"
                }
            else:
                # Both failed, provide detailed error
                if "No module named" in output_text2 or "DJANGO_SETTINGS_MODULE" in output_text2:
                    return {
                        "success": False,
                        "message": f"Django configuration error: The script requires a properly configured Django project. Please ensure you have uploaded a valid Django project and extracted it first. Simplified script output: {output_text[:100]}... Original script error: {output_text2[:100]}..."
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Both scripts failed. Simplified: {output_text[:100]}... Original: {output_text2[:100]}..."
                    }

    except Exception as e:
        import traceback
        print(f"Error executing import diagram: {str(e)}")
        print(traceback.format_exc())
        return {
            "success": False,
            "message": f"Error executing import diagram: {str(e)}"
        }
