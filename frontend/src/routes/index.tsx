import { chatbotOpenAtom } from "$lib/features/chatbot/atoms";
import { Alert, Button, CircularProgress, Divider, Modal, ModalClose, ModalDialog, Snackbar, Typography } from "@mui/joy";
import axios from "axios";
import { useAtom } from "jotai";
import { Bot, Box, Code, MessageSquare, Upload } from "lucide-react";
import React, { useState } from "react";

export const IndexPage: React.FC = () => {
    const [, setChatbot] = useAtom(chatbotOpenAtom);
    const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string; extract_path?: string } | null>(null);
    const [showSnackbar, setShowSnackbar] = useState(false);
    const [jinjaResult, setJinjaResult] = useState<{ success: boolean; message: string; diagram_json?: string } | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [openModal, setOpenModal] = useState(false);

    const handleZipUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file && file.type === "application/zip") {
            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await axios.post('http://api.ai4mde.localhost/api/v1/utils/upload-zip', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });

                setUploadResult(response.data);
                setShowSnackbar(true);
                console.log("Zip file uploaded:", response.data);
            } catch (error) {
                console.error("Upload failed:", error);
                setUploadResult({
                    success: false,
                    message: "Upload failed, please check API connection"
                });
                setShowSnackbar(true);
            }
        }
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

        setIsLoading(true);

        try {
            const response = await axios.post('http://api.ai4mde.localhost/api/v1/utils/extract-jinja', {
                extract_path: uploadResult.extract_path
            });

            setJinjaResult(response.data);
            setShowSnackbar(true);

            if (response.data.success && response.data.diagram_json) {
                setOpenModal(true);
            }

            console.log("Jinja extracted:", response.data);
        } catch (error) {
            console.error("Extraction failed:", error);
            setJinjaResult({
                success: false,
                message: "Jinja extraction failed, please check API connection"
            });
            setShowSnackbar(true);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCloseSnackbar = () => {
        setShowSnackbar(false);
    };

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
                        component="label"
                        htmlFor="upload-zip"
                    >
                        <Upload size={20} />
                        <span className="pl-2">Upload zip file</span>
                        <input
                            id="upload-zip"
                            type="file"
                            accept=".zip"
                            onChange={handleZipUpload}
                            style={{ display: "none" }}
                        />
                    </Button>
                </div>

                {uploadResult && uploadResult.success && (
                    <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                        <h4 className="font-medium">File Upload Successful</h4>
                        <p className="text-sm mt-1">Extraction Path: {uploadResult.extract_path}</p>

                        <div className="mt-3 flex gap-2">
                            <Button
                                startDecorator={<Code size={16} />}
                                onClick={handleExtractJinja}
                                disabled={isLoading}
                                color="primary"
                                variant="solid"
                            >
                                {isLoading ? (
                                    <>
                                        <CircularProgress size="sm" />
                                        <span className="pl-2">Processing...</span>
                                    </>
                                ) : "Extract Jinja"}
                            </Button>
                        </div>
                    </div>
                )}

                {jinjaResult && jinjaResult.success && !openModal && (
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                        <h4 className="font-medium">Jinja Extraction Successful</h4>
                        <p className="text-sm mt-1">{jinjaResult.message}</p>
                        <Button
                            size="sm"
                            variant="outlined"
                            onClick={() => setOpenModal(true)}
                            className="mt-2"
                        >
                            View JSON Data
                        </Button>
                    </div>
                )}
            </div>

            <Snackbar
                open={showSnackbar}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert
                    variant="outlined"
                    color={(uploadResult?.success || jinjaResult?.success) ? "success" : "danger"}
                    endDecorator={
                        <Button variant="plain" size="sm" onClick={handleCloseSnackbar}>
                            Close
                        </Button>
                    }
                >
                    {jinjaResult?.message || uploadResult?.message}
                </Alert>
            </Snackbar>

            <Modal open={openModal} onClose={() => setOpenModal(false)}>
                <ModalDialog
                    variant="outlined"
                    size="lg"
                    sx={{
                        width: '80%',
                        maxWidth: '900px',
                        maxHeight: '80vh',
                        overflow: 'auto'
                    }}
                >
                    <ModalClose onClick={() => setOpenModal(false)} />
                    <Typography level="h4" component="h2" className="mb-4">
                        Extracted Diagram JSON
                    </Typography>

                    <div className="bg-gray-100 p-4 rounded overflow-auto max-h-[500px]">
                        <pre className="text-xs whitespace-pre-wrap">
                            {jinjaResult?.diagram_json && JSON.stringify(JSON.parse(jinjaResult.diagram_json), null, 2)}
                        </pre>
                    </div>

                    <div className="mt-4 flex justify-end">
                        <Button
                            color="primary"
                            onClick={() => {
                                if (jinjaResult?.diagram_json) {
                                    const blob = new Blob([jinjaResult.diagram_json], { type: 'application/json' });
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = 'diagram.json';
                                    document.body.appendChild(a);
                                    a.click();
                                    document.body.removeChild(a);
                                    URL.revokeObjectURL(url);
                                }
                            }}
                        >
                            Download JSON
                        </Button>
                    </div>
                </ModalDialog>
            </Modal>
        </div>
    );
};

export default IndexPage;
