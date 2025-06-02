import { chatbotOpenAtom } from "$lib/features/chatbot/atoms";
import { Alert, Button, Divider, FormControl, FormLabel, Input, Modal, ModalClose, ModalDialog, Option, Select, Snackbar, Switch, Typography } from "@mui/joy";
import axios from "axios";
import { useAtom } from "jotai";
import { Bot, Box, MessageSquare, Settings } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";

export const IndexPage: React.FC = () => {
    const [, setChatbot] = useAtom(chatbotOpenAtom);
    const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string; extract_path?: string } | null>(null);
    const [UploadFileName, setUploadFileName] = useState("No file selected");
    const [showSnackbar, setShowSnackbar] = useState(false);
    const [jinjaResult, setJinjaResult] = useState<{ success: boolean; message: string; diagram_json?: string } | null>(null);
    const [importResult, setImportResult] = useState<{ success: boolean; message: string; } | null>(null);
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
            const response = await axios.post('http://api.ai4mde.localhost/api/v1/utils/upload-zip', formData, {
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
                ? `Error: ${error.response.status} - ${error.response.data?.message || JSON.stringify(error.response.data)}`
                : `Error: ${error.message || 'Unknown error'}`;

            console.error("Detailed error:", errorMessage);

            setUploadResult({
                success: false,
                message: `Upload failed: ${errorMessage}`
            });
            setShowSnackbar(true);
        } finally {
            setIsUploading(false);
            // Reset file inputs
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleZipUpload = () => {
        fileInputRef.current?.click();
    };

    const handleExtractJinja = async () => {
        if (!uploadResult?.extract_path) {
            setJinjaResult({
                success: false,
                message: "No extraction path available. Please upload a ZIP file first."
            });
            setShowSnackbar(true);
            return;
        }

        console.log("There is a zip file:", uploadResult?.extract_path);

        var project_id = selectedProjectId
        var system_id = selectedSystemId

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
            const response = await axios.post('http://api.ai4mde.localhost/api/v1/utils/extract-jinja', {
                extract_path: uploadResult.extract_path,
                project_id: project_id,
                system_id: system_id,
                include_method_dependencies: includeMethodDependency
            });

            if (response.data.success && response.data.diagram_json) {
                setJinjaResult({
                    success: true,
                    message: "Extraction succesful",
                    diagram_json: response.data
                });
                console.log("Jinja extracted:", response.data);
                return response.data.diagram_json;
            }
            else {
                console.error("Extraction failed:", response.data.message);
                setJinjaResult({
                    success: false,
                    message: response.data.message
                });
                setShowSnackbar(true);
            }

        } catch (error) {
            console.error("Extraction failed:", error);
            setJinjaResult({
                success: false,
                message: "Jinja extraction failed, please check API connection"
            });
            setShowSnackbar(true);
        }
    };

    const handleCloseSnackbar = () => {
        setShowSnackbar(false);
    };

    useEffect(() => {
        if (popupOpen) {
            axios.get("http://api.ai4mde.localhost/api/v1/metadata/projects/")
                .then((res) => setProjects(res.data))
                .catch((err) => console.error("Failed to fetch projects", err));
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
                const layoutResponse = await axios.post(layout_url, diagram);
            }

            setImportResult({
                success: true,
                message: "Import successful! Go to the corresponding project so you view the diagram",
            });
            setShowSnackbar(true);

        } catch (error: any) {
            if (error.response) {
                console.log(`Import request failed with status ${error.response.status}: ${error.response.data}`);
            } else if (error.request) {
                console.log("No response received from the server.");
            } else {
                console.log(`Import request failed: ${error.message}`);
            }
        }
    };

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
                    <Button onClick={() => setPopupOpen(true)}>
                        <span className="pl-2">Import via zip file</span>
                    </Button>
                </div>
            </div>

            <Snackbar
                open={showSnackbar}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert
                    variant="outlined"
                    color={((uploadResult?.success && jinjaResult?.success) || uploadResult?.success && jinjaResult?.success === undefined) ? "success" : "danger"}
                    endDecorator={
                        <Button variant="plain" size="sm" onClick={handleCloseSnackbar}>
                            Close
                        </Button>
                    }
                >
                    {!jinjaResult?.success && jinjaResult?.message || importResult?.message}
                </Alert>
            </Snackbar>

            <Modal open={popupOpen} onClose={() => setPopupOpen(false)}>
                <ModalDialog>
                    <ModalClose />
                    <Typography level="h4">Import Diagram</Typography>
                    <FormControl fullWidth sx={{ mt: 2 }}>
                        <FormLabel>1. Upload .zip file</FormLabel>

                        <div className="flex items-center gap-4">
                            <Typography level="body-sm">
                                {UploadFileName}
                            </Typography>
                            <Button
                                component="label"
                                variant="soft"
                                color="primary"
                                onClick={handleZipUpload}
                            >
                                Upload ZIP File
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    onChange={handleFileUpload}
                                    style={{ display: "none" }}
                                />
                            </Button>
                        </div>

                    </FormControl>

                    <FormControl fullWidth sx={{ mt: 2 }}>
                        <FormLabel>2. Select Project</FormLabel>
                        <Select
                            value={selectedProjectId}
                            onChange={(e, newValue) => {
                                setSelectedProjectId(newValue);
                                setSelectedSystemId("");
                                setIsCreatingNewProject(newValue === "new");
                            }}
                            placeholder="Select a project"
                        >
                            {projects.map((project) => (
                                <Option key={project.id} value={project.id}>
                                    {project.name}
                                </Option>
                            ))}
                            <Option value="new">+ Create new project</Option>
                        </Select>
                    </FormControl>

                    {isCreatingNewProject && (
                        <>
                            <FormControl fullWidth sx={{ mt: 2 }}>
                                <FormLabel>2a. Project Name</FormLabel>
                                <Input
                                    placeholder="Enter new project name"
                                    value={newProjectName}
                                    onChange={(e) => setNewProjectName(e.target.value)}
                                />
                            </FormControl>
                            <FormControl fullWidth sx={{ mt: 2 }}>
                                <FormLabel>2b. System Name</FormLabel>
                                <Input
                                    placeholder="Enter new system name"
                                    value={newSystemName}
                                    onChange={(e) => setNewSystemName(e.target.value)}
                                />
                            </FormControl>
                        </>
                    )}

                    {!isCreatingNewProject && (
                        <FormControl fullWidth sx={{ mt: 2 }}>
                            <FormLabel>3. Select System</FormLabel>
                            <Select
                                value={selectedSystemId}
                                onChange={(e, newValue) => {
                                    setSelectedSystemId(newValue);
                                    setIsCreatingNewSystem(newValue === "new");
                                }}
                                placeholder="Select a system"
                            >
                                {systems.map((system) => (
                                    <Option key={system.id} value={system.id}>
                                        {system.name}
                                    </Option>
                                ))}
                                <Option value="new">+ Create new system</Option>
                            </Select>
                        </FormControl>
                    )}

                    {!isCreatingNewProject && isCreatingNewSystem && (
                        <FormControl fullWidth sx={{ mt: 2 }}>
                            <FormLabel>3a. System Name</FormLabel>
                            <Input
                                placeholder="Enter new system name"
                                value={newSystemName}
                                onChange={(e) => setNewSystemName(e.target.value)}
                            />
                        </FormControl>
                    )}

                    <FormControl orientation="horizontal" sx={{ justifyContent: 'space-between' }}>
                        <div>
                            <FormLabel>
                                <Settings size={16} className="inline mr-2" />
                                Include Method Dependencies
                            </FormLabel>
                            <Typography level="body-sm" className="text-gray-600">
                                Include method dependencies in the diagram generation
                            </Typography>
                        </div>
                        <Switch
                            checked={includeMethodDependency}
                            onChange={(event) => setIncludeMethodDependency(event.target.checked)}
                            color={includeMethodDependency ? 'success' : 'neutral'}
                        />
                    </FormControl>

                    <div className="flex justify-end gap-2 mt-4">
                        <Button variant="plain"
                            onClick={() => {
                                setPopupOpen(false)
                                setIsImporting(false);
                            }}>
                            Cancel
                        </Button>
                        <Button
                            loading={isImporting}
                            onClick={async () => {
                                setIsImporting(true);
                                const result = await handleExtractJinja();

                                if (result) {
                                    await handleImport(JSON.stringify(JSON.parse(result), null, 2));
                                }

                                setIsImporting(false);
                                setPopupOpen(false)
                            }}
                            disabled={!canImport || isImporting}
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
