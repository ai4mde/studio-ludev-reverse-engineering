from diagram.api import diagram_router
from django.http import HttpResponse
import os
import zipfile
import sys
import json
import inspect
import uuid
from datetime import datetime
from pathlib import Path
from metadata.api import metadata_router
from prose.api import prose_router
from generator.api import generator_router
from ninja import NinjaAPI, Schema, File
from ninja.files import UploadedFile
from jinja2 import Template
from django.apps import apps
from django.db import models

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


class ExtractJinjaResponse(Schema):
    success: bool
    message: str
    diagram_json: str = None


# Jinja2 template, same as extract_jinja2.py
json_template = """
{
    "diagrams": [
        {
            "id": "{{ diagram_id }}",
            "name": "Diagram",
            "type": "classes",
            "edges": [
                {% for edge in edges %}
                {
                    "id": "{{ edge.id }}",
                    "rel": {
                        "type": "{{ edge.rel.type }}",
                        "label": "{{ edge.rel.label }}",
                        "multiplicity": {
                            "source": "{{ edge.rel.multiplicity.source }}",
                            "target": "{{ edge.rel.multiplicity.target }}"
                        }
                    },
                    "data": {},
                    "rel_ptr": "{{ edge.rel_ptr }}",
                    "source_ptr": "{{ edge.source_ptr }}",
                    "target_ptr": "{{ edge.target_ptr }}"
                }
                {% if not loop.last %},{% endif %}
                {% endfor %}
            ],
            "nodes": [
                {% for node in nodes %}
                {
                    "id": "{{ node.id }}",
                    "cls": {
                        "leaf": false,
                        "name": "{{ node.cls.name }}",
                        "type": "class",
                        "methods": [
                            {% for method in node.cls.methods %}
                            {
                                "body": "",
                                "name": "{{ method.name }}",
                                "type": "{{ method.type }}",
                                "description": ""
                            }
                            {% if not loop.last %},{% endif %}
                            {% endfor %}
                        ],
                        "abstract": false,
                        "namespace": "",
                        "attributes": [
                            {% for attribute in node.cls.attributes %}
                            {
                                "body": null,
                                "enum": null,
                                "name": "{{ attribute.name }}",
                                "type": "{{ attribute.type }}",
                                "derived": false,
                                "description": null
                            }
                            {% if not loop.last %},{% endif %}
                            {% endfor %}
                        ]
                    },
                    "data": {
                        "position": {
                            "x": {{ node.data.position.x }},
                            "y": {{ node.data.position.y }}
                        }
                    },
                    "cls_ptr": "{{ node.cls_ptr }}"
                }
                {% if not loop.last %},{% endif %}
                {% endfor %}
            ],
            "system": "{{ system_id }}",
            "project": "{{ project_id }}",
            "description": ""
        }
    ]
}
"""

# Define the Django generated method set
DJANGO_GENERATED_METHODS = set([
    'check',
    'clean',
    'clean_fields',
    'delete',
    'full_clean',
    'save',
    'save_base',
    'validate_unique'
])


# Get the custom methods of the model
def get_custom_methods(model):
    custom_methods = []
    standard_methods = set(dir(models.Model))
    for m in dir(model):
        if m.startswith('_') or m in standard_methods:
            continue
        if m in DJANGO_GENERATED_METHODS:
            continue
        if is_method_without_args(getattr(model, m)):
            custom_methods.append(m)
    return custom_methods


# Check if the method has no parameters
def is_method_without_args(func):
    """Check if func is a method callable with only one param (self)"""
    if not inspect.isfunction(func) and not inspect.ismethod(func):
        return False
    sig = inspect.signature(func)
    params = sig.parameters

    # Check if there is exactly one parameter and that has the name 'self'
    return len(params) == 1 and 'self' in params


@api.post("/utils/extract-jinja", response=ExtractJinjaResponse, tags=["utils"])
def extract_jinja(request, data: ExtractJinjaRequest):
    try:
        extract_path = data.extract_path
        
        # Add the project path to sys.path
        sys.path.append(extract_path)
        
        # Find the settings.py file
        settings_files = list(Path(extract_path).glob('**/settings.py'))
        if not settings_files:
            return {
                "success": False, 
                "message": "No Django settings.py file found in the extracted directory"
            }
        
        # Get the project root directory
        project_root = settings_files[0].parent
        project_name = project_root.name
        
        # Set the Django environment
        os.environ['DJANGO_SETTINGS_MODULE'] = f"{project_name}.settings"
        
        # Import and configure Django
        import django
        django.setup()
        
        # Generate the diagram JSON
        diagram_json = generate_diagram_json()
        
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


# Function to generate the diagram JSON
def generate_diagram_json():
    diagrams = []
    edges = []
    nodes = []

    # Define the diagram ID, system ID, and project ID
    diagram_id = str(uuid.uuid4())
    system_id = "c79c758a-d2c5-4e2c-bf71-eadcaf769299"
    project_id = "99fc3c09-07bc-43d2-bf59-429f99a35839"

    # Iterate through all installed applications and process models
    for app_config in apps.get_app_configs():
        # Process all models of the application, not only shared_models
        print(f"Extracting models from: {app_config.name}")

        # Get all models in the application
        models_list = app_config.get_models()

        # Process each model
        for model in models_list:
            # Create a node for each model
            model_node = {
                "id": str(uuid.uuid4()),  # The unique ID of the node
                "cls": {
                    "leaf": False,
                    "name": model.__name__,
                    "type": "class",
                    "methods": [],
                    "abstract": False,
                    "namespace": "",
                    "attributes": []
                },
                "data": {
                    "position": {"x": 0, "y": 0}  # The placeholder for the position
                },
                "cls_ptr": str(uuid.uuid4())  # The pointer ID of the class
            }

            # Extract methods
            for name in get_custom_methods(model):
                model_node["cls"]["methods"].append({
                    "body": "",
                    "name": name,
                    "type": "function",
                    "description": ""
                })

            # Extract attributes (fields)
            for field in model._meta.get_fields():
                model_node["cls"]["attributes"].append({
                    "body": None,
                    "enum": None,
                    "name": field.name,
                    "type": field.get_internal_type().lower(),
                    "derived": False,
                    "description": None
                })

            # Add the node to the diagram
            nodes.append(model_node)

            # Check relations (like foreign key, many-to-many)
            for field in model._meta.get_fields():
                if field.is_relation:
                    # Process foreign key or one-to-many or many-to-many relations
                    if field.many_to_one:
                        edge = {
                            "id": str(uuid.uuid4()),
                            "rel": {
                                "type": "association",
                                "label": "in",
                                "multiplicity": {
                                    "source": "0..1",
                                    "target": "1"
                                }
                            },
                            "rel_ptr": str(uuid.uuid4()),
                            "source_ptr": model_node["cls_ptr"],
                            "target_ptr": str(uuid.uuid4())
                        }
                        edges.append(edge)

                    if field.one_to_many:
                        edge = {
                            "id": str(uuid.uuid4()),
                            "rel": {
                                "type": "association",
                                "label": "has",
                                "multiplicity": {
                                    "source": "1",
                                    "target": "1"
                                }
                            },
                            "rel_ptr": str(uuid.uuid4()),
                            "source_ptr": model_node["cls_ptr"],
                            "target_ptr": str(uuid.uuid4())
                        }
                        edges.append(edge)

                    if field.many_to_many:
                        edge = {
                            "id": str(uuid.uuid4()),
                            "rel": {
                                "type": "association",
                                "label": "has",
                                "multiplicity": {
                                    "source": "1",
                                    "target": "0..n"
                                }
                            },
                            "rel_ptr": str(uuid.uuid4()),
                            "source_ptr": model_node["cls_ptr"],
                            "target_ptr": str(uuid.uuid4())
                        }
                        edges.append(edge)

    # Create the final JSON structure
    template = Template(json_template)
    rendered_json = template.render(
        diagram_id=diagram_id,
        edges=edges,
        nodes=nodes,
        system_id=system_id,
        project_id=project_id
    )

    return rendered_json
