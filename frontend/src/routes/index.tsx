import { chatbotOpenAtom } from "$lib/features/chatbot/atoms";
import { Alert, Button, Divider, FormControl, FormLabel, Input, Modal, ModalClose, ModalDialog, Option, Select, Snackbar, Switch, Tooltip, Typography } from "@mui/joy";
import axios from "axios";
import { useAtom } from "jotai";
import { Bot, Box, Import, MessageSquare, Settings, Upload, X } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";

export const IndexPage: React.FC = () => {
    const [, setChatbot] = useAtom(chatbotOpenAtom);
    const [uploadResult, setUploadResult] = useState<{ success: boolean; extract_path?: string } | null>(null);
    const [UploadFileName, setUploadFileName] = useState("No file selected");
    const [showSnackbar, setShowSnackbar] = useState(false);
    const [message, setMessage] = useState<{ isError: boolean; header: string; message: string; } | null>(null);
    const [popupOpen, setPopupOpen] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [isImporting, setIsImporting] = useState(false);
    const [projects, setProjects] = useState([]);
    const [systems, setSystems] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState("");
    const [selectedSystemId, setSelectedSystemId] = useState("");
    const [isCreatingNewProject, setIsCreatingNewProject] = useState(false);
    const [isCreatingNewSystem, setIsCreatingNewSystem] = useState(false);
    const [newProjectName, setNewProjectName] = useState("");
    const [newSystemName, setNewSystemName] = useState("");
    const [isDragOver, setIsDragOver] = useState(false);
    const [toolTipOpen, setToolTipOpen] = useState(true);

    const [includeMethodDependency, setIncludeMethodDependency] = useState(false);

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        setIsUploading(true);
        setUploadProgress(0);

        try {
            const formData = new FormData();

            // 确定上传类型：ZIP文件还是文件夹
            const isZipUpload = files[0].type === "application/zip" || "x-zip-compressed";
            console.log("Upload type:", isZipUpload ? "ZIP" : "Folder");
            console.log("Number of files:", files.length);

            if (isZipUpload) {
                // Zip file upload
                formData.append('file', files[0]);
                console.log("ZIP upload - file added to form:", files[0].name);
                setUploadFileName(files[0].name);
            } else {
                // Folder upload (multiple files)
                console.log("Folder upload - files to process:", files.length);

                // 明确设置为文件夹上传
                formData.append('is_zip', 'false');

                // 添加每个文件到formData，保留相对路径
                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    const path = file.webkitRelativePath || file.name;
                    console.log(`Adding file ${i + 1}/${files.length}:`, path);

                    // 使用相对路径作为文件名
                    formData.append(`files[${i}]`, file, path);
                }
            }

            console.log("Starting upload...");
            const response = await axios.post('http://api.ai4mde.localhost/api/v1/importer/importer/upload_zip', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total) {
                        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                        setUploadProgress(percentCompleted);
                        console.log(`Upload progress: ${percentCompleted}%`);
                    }
                }
            });

            console.log("Upload response:", response.data);
            setUploadResult(response.data);
            console.log("Zip file uploaded:", response.data);
        } catch (error) {
            console.error("Upload failed:", error);
            // 显示更详细的错误信息
            const errorMessage = error.response
                ? `Error: HTTP ${error.response.status} `
                : `Error: ${error.message || 'Unknown error'}`;

            console.error("Detailed error:", errorMessage);

            setMessage({
                isError: true,
                header: `Upload failed: ${error.code}`,
                message: `Upload request failed: ${error.message}.`
            });
            setShowSnackbar(true);
        } finally {
            setIsUploading(false);
            // Reset file inputs
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleFileDrop = async (files: FileList) => {
        if (!files || files.length === 0) return;

        const file = files[0];
        setUploadFileName(file.name);

        // 创建一个模拟的事件对象
        const mockEvent = {
            target: {
                files: files
            }
        } as React.ChangeEvent<HTMLInputElement>;

        await handleFileUpload(mockEvent);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            handleFileDrop(files);
        }
    };

    const handleZipUpload = () => {
        fileInputRef.current?.click();
    };

    const handleClearUpload = () => {
        setUploadResult(null);
        setUploadFileName("No file selected");
        setUploadProgress(0);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleTooltipOpen = () => {
        setToolTipOpen(true);
    };

    const handleTooltipClose = () => {
        setToolTipOpen(false);

    };

    const handleExtractJinja = async () => {
        if (!uploadResult?.extract_path) {
            setMessage({
                isError: true,
                header: "No extraction path available",
                message: "Please upload a ZIP file first."
            });
            setShowSnackbar(true);
            return;
        }

        console.log("There is a zip file:", uploadResult?.extract_path);

        let project_id = selectedProjectId
        let system_id = selectedSystemId

        if (isCreatingNewProject) {
            const response = await axios.post('http://api.ai4mde.localhost/api/v1/metadata/projects/', {
                name: newProjectName,
                description: "",
            });

            setSelectedProjectId(response.data.id)
            project_id = response.data.id

            const response2 = await axios.post('http://api.ai4mde.localhost/api/v1/metadata/systems/', {
                project: response.data.id,
                name: newSystemName,
                description: "",
            });

            setSelectedSystemId(response2.data.id)
            system_id = response2.data.id
        }

        if (isCreatingNewSystem) {
            const response2 = await axios.post('http://api.ai4mde.localhost/api/v1/metadata/systems/', {
                project: selectedProjectId,
                name: newSystemName,
                description: "",
            });

            setSelectedSystemId(response2.data.id)
            system_id = response2.data.id
        }

        console.log("Executing extraction script");

        try {
            const response = await axios.post('http://api.ai4mde.localhost/api/v1/importer/importer/extract_jinja', {
                extract_path: uploadResult.extract_path,
                project_id: project_id,
                system_id: system_id,
                include_method_dependencies: includeMethodDependency
            });

            if (response.data.success && response.data.diagram_json) {
                console.log("Jinja extracted:", response.data);
                return response.data.diagram_json;
            }
            else {
                console.error("Extraction failed:", response.data.message);
                setMessage({
                    isError: true,
                    header: "Extraction failed",
                    message: response.data.message
                });
                setShowSnackbar(true);
            }

        } catch (error) {
            console.error("Extraction failed:", error);
            setMessage({
                isError: true,
                header: "Extraction failed",
                message: "Jinja extraction failed, please check API connection"
            });
            setShowSnackbar(true);
        }
    };

    const handleCloseSnackbar = () => {
        setShowSnackbar(false);
    };

    const clearSettings = () => {
        setSelectedProjectId("");
        setSelectedSystemId("");
        setIsCreatingNewProject(false);
        setIsCreatingNewSystem(false);
        setIsImporting(false);
        handleClearUpload();
        setIncludeMethodDependency(false);
        setToolTipOpen(false);
        setMessage(null)
    }

    useEffect(() => {
        if (popupOpen) {
            axios.get("http://api.ai4mde.localhost/api/v1/metadata/projects/")
                .then((res) => setProjects(res.data))
                .catch((err) => console.error("Failed to fetch projects", err));
        } else {
            clearSettings();
        }
    }, [popupOpen]);

    useEffect(() => {
        if (selectedProjectId && selectedProjectId !== "new") {
            axios.get(`http://api.ai4mde.localhost/api/v1/metadata/systems?project=${selectedProjectId}`)
                .then((res) => setSystems(res.data))
                .catch((err) => console.error("Failed to fetch systems", err));
        } else {
            setSystems([]);
        }
    }, [selectedProjectId]);


    const handleImport = async (diagram: string) => {
        console.log("Importing diagram");
        try {
            const importResponse = await axios.post("http://api.ai4mde.localhost/api/v1/diagram/import", diagram, { headers: { 'Content-Type': 'application/json' } });
            if (importResponse.status === 200) {
                const diagram_id = importResponse.data.id;
                const layout_url = "http://api.ai4mde.localhost/api/v1/diagram/" + diagram_id + "/auto_layout";
                await axios.post(layout_url, diagram);
            }

            setMessage({
                isError: false,
                header: "Import successful!",
                message: "Go to the corresponding project so you view the diagram",
            });
            setShowSnackbar(true);
            console.log("Import succesful");
            return true;
        } catch (error: any) {
            console.error("Import failed:", error);
            const errorMessage = error.response
                ? `Error: HTTP ${error.response.status} `
                : `Error: ${error.message || 'Unknown error'}`;

            console.error("Detailed error:", errorMessage);

            setMessage({
                isError: true,
                header: `Import failed: ${error.code}`,
                message: `Import request failed: ${error.message}.`
            });
            setShowSnackbar(true);
        }
    };

    const handleImportWrapper = async () => {
        setIsImporting(true);
        const extractionResponse = await handleExtractJinja();
        if (extractionResponse) {
            const importResponse = handleImport(JSON.stringify(JSON.parse(extractionResponse), null, 2));
            setIsImporting(false);
            if (importResponse) {
                setPopupOpen(false);
            }
        }
    }

    const canImport = isCreatingNewProject
        ? newProjectName.trim() !== "" && newSystemName.trim() !== ""
        : isCreatingNewSystem
            ? newSystemName.trim() !== ""
            : selectedProjectId && selectedSystemId;

    return (
        <div className="grid grid-cols-12 p-3 gap-3 w-full">
            <div className="p-4 col-span-12 flex flex-col gap-4 rounded-lg bg-gray-100">
                <div className="flex flex-col gap-1">
                    <h1 className="text-2xl font-semibold">
                        Welcome to AI4MDE Studio
                    </h1>
                    <h3 className="text-xl">
                        Build applications through conversation
                    </h3>
                </div>
                <Divider />
                <div className="flex flex-row gap-2">
                    <Button component="a" href="/build">
                        <Bot size={20} />
                        <span className="pl-2">Import a requirements text</span>
                    </Button>
                    <Button onClick={() => setChatbot(true)}>
                        <MessageSquare size={20} />
                        <span className="pl-2">
                            Start chatting with our chatbot
                        </span>
                    </Button>
                    <Button component="a" href="/projects">
                        <Box size={20} />
                        <span className="pl-2">
                            Create a project & system by hand
                        </span>
                    </Button>
                    <Button
                        component="a"
                        onClick={() => setPopupOpen(true)}>
                        <Import size={20} />
                        <span className="pl-2">Import via zip file</span>
                    </Button>
                </div>
            </div>

            <Snackbar
                open={showSnackbar}
                autoHideDuration={!message?.isError ? null : 15000}
                onClose={handleCloseSnackbar}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert
                    variant="outlined"
                    color={!message?.isError ? "success" : "danger"}
                    endDecorator={
                        <Button variant="plain" size="sm" onClick={handleCloseSnackbar}>
                            Close
                        </Button>
                    }
                >
                    {message !== null &&
                        <div>
                            <Typography level="title-lg">{message?.header}</Typography>
                            <Typography level="body-sm">{message?.message}</Typography>
                        </div>}
                </Alert>
            </Snackbar>

            <Modal open={popupOpen} onClose={() => setPopupOpen(false)}>
                <ModalDialog sx={{ width: 1 / 3 }}>
                    <ModalClose />
                    <Typography level="h4">Import Diagram</Typography>
                    <FormControl sx={{ mt: 2 }}>
                        <FormLabel>1. Upload Django Project</FormLabel>

                        <div
                            className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors relative ${isDragOver
                                ? 'border-blue-400 bg-blue-50'
                                : isUploading
                                    ? 'border-gray-300 bg-gray-50'
                                    : uploadResult?.success
                                        ? 'border-green-400 bg-green-50'
                                        : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                                }`}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            onClick={!isUploading && !uploadResult?.success ? handleZipUpload : undefined}
                        >
                            {uploadResult?.success && (
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        clearSettings();
                                    }}
                                    className="absolute top-2 right-2 p-1 rounded-full bg-red-100 hover:bg-red-200 text-red-600 transition-colors"
                                    title="Clear upload"
                                >
                                    <X size={16} />
                                </button>
                            )}

                            {isUploading ? (
                                <div className="flex flex-col items-center gap-2">
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-blue-600 h-2 rounded-full transition-all"
                                            style={{ width: `${uploadProgress}%` }}
                                        ></div>
                                    </div>
                                    <Typography level="body-sm">
                                        Uploading... {uploadProgress}%
                                    </Typography>
                                </div>
                            ) : uploadResult?.success ? (
                                <div className="flex flex-col items-center gap-3">
                                    <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full">
                                        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                    <div>
                                        <Typography level="body-md" className="font-medium text-green-700">
                                            Upload Successful!
                                        </Typography>
                                        <Typography level="body-sm" className="text-gray-600 mt-1">
                                            File: {UploadFileName}
                                        </Typography>
                                        <Typography level="body-sm" className="text-gray-500 mt-1">
                                            Click the × button to upload a different file
                                        </Typography>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-3">
                                    <Upload size={32} className="text-gray-400" />
                                    <div>
                                        <Typography level="body-md" className="font-medium">
                                            {isDragOver ? 'Drop your ZIP file here' : 'Drag & drop your ZIP file here'}
                                        </Typography>
                                        <Typography level="body-sm" className="text-gray-500 mt-1">
                                            or click to browse files
                                        </Typography>
                                    </div>
                                    {UploadFileName !== "No file selected" && (
                                        <Typography level="body-sm" className="text-blue-600 font-medium">
                                            Selected: {UploadFileName}
                                        </Typography>
                                    )}
                                </div>
                            )}

                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".zip"
                                onChange={handleFileUpload}
                                style={{ display: "none" }}
                            />
                        </div>
                    </FormControl>

                    <FormControl sx={{ mt: 2 }}>
                        <FormLabel>2. Select Project</FormLabel>
                        <Tooltip title={uploadResult ?
                            "Select the project you want the import to be added to" : "Upload a Django project first"}
                            size="md"
                            placement="bottom"
                            disableHoverListener={!toolTipOpen}
                        >
                            <span>
                                <Select
                                    disabled={!uploadResult}
                                    value={selectedProjectId}
                                    onChange={(e, newValue) => {
                                        setSelectedProjectId(newValue);
                                        setSelectedSystemId("");
                                        setIsCreatingNewProject(newValue === "new");
                                        handleTooltipOpen();
                                    }}
                                    placeholder="Select a project"
                                    onClose={handleTooltipOpen}
                                    onListboxOpenChange={handleTooltipClose}
                                >
                                    {projects.map((project) => (
                                        <Option key={project.id} value={project.id}>
                                            {project.name}
                                        </Option>
                                    ))}
                                    <Option value="new">+ Create new project and system</Option>
                                </Select>
                            </span>
                        </Tooltip>
                    </FormControl>

                    {isCreatingNewProject && (
                        <>
                            <FormControl sx={{ mt: 2 }}>
                                <FormLabel>Project Name</FormLabel>
                                <Input
                                    placeholder="Enter new project name"
                                    value={newProjectName}
                                    onChange={(e) => setNewProjectName(e.target.value)}
                                />
                            </FormControl>
                            <FormControl sx={{ mt: 2 }}>
                                <FormLabel>System Name</FormLabel>
                                <Input
                                    placeholder="Enter new system name"
                                    value={newSystemName}
                                    onChange={(e) => setNewSystemName(e.target.value)}
                                />
                            </FormControl>
                        </>
                    )}

                    {!isCreatingNewProject && (
                        <Tooltip title={selectedProjectId ?
                            "Select the system you want the import to be added to" : "Select or create a project first"}
                            size="md"
                            placement="bottom"
                            disableHoverListener={!toolTipOpen}
                        >
                            <span>
                                <FormControl sx={{ mt: 3 }}>
                                    <FormLabel>3. Select System</FormLabel>
                                    <Select
                                        disabled={!selectedProjectId}
                                        value={selectedSystemId}
                                        onChange={(e, newValue) => {
                                            setSelectedSystemId(newValue);
                                            setIsCreatingNewSystem(newValue === "new");
                                            handleTooltipOpen();
                                        }}
                                        placeholder="Select a system"
                                        onClose={handleTooltipOpen}
                                        onListboxOpenChange={handleTooltipClose}
                                    >
                                        {systems.map((system) => (
                                            <Option key={system.id} value={system.id}>
                                                {system.name}
                                            </Option>
                                        ))}
                                        <Option value="new">+ Create new system</Option>
                                    </Select>
                                </FormControl>
                            </span>
                        </Tooltip>
                    )}

                    {!isCreatingNewProject && isCreatingNewSystem && (
                        <FormControl sx={{ mt: 2 }}>
                            <FormLabel>System Name</FormLabel>
                            <Input
                                placeholder="Enter new system name"
                                value={newSystemName}
                                onChange={(e) => setNewSystemName(e.target.value)}
                            />
                        </FormControl>
                    )}
                    <Typography sx={{ mt: 5, fontSize: 10 }}>
                        Advanced settings
                    </Typography>
                    <Divider />
                    <FormControl orientation="horizontal" sx={{ justifyContent: 'space-between' }}>
                        <div>
                            <FormLabel>
                                <Settings size={16} className="inline mr-2" />
                                Include Method Dependencies
                            </FormLabel>
                            <Typography sx={{ fontSize: 10 }}>
                                Include method dependencies in the diagram generation.
                            </Typography>
                        </div>
                        <Switch
                            checked={includeMethodDependency}
                            onChange={(event) => setIncludeMethodDependency(event.target.checked)}
                            color={includeMethodDependency ? 'success' : 'neutral'}
                        />
                    </FormControl>

                    <div className="flex justify-end gap-2 margin-4">
                        <Button variant="plain"
                            onClick={() => {
                                setPopupOpen(false)
                            }}>
                            Cancel
                        </Button>
                        <Button
                            loading={isImporting && !message?.isError}
                            onClick={handleImportWrapper}
                            disabled={!canImport || isImporting || message?.isError}
                        >
                            Import Diagram
                        </Button>
                    </div>
                </ModalDialog>
            </Modal>
        </div>
    );
};

export default IndexPage;