import { chatbotOpenAtom } from "$lib/features/chatbot/atoms";
import { Alert, Button, Divider, Snackbar } from "@mui/joy";
import axios from "axios";
import { useAtom } from "jotai";
import { Bot, Box, MessageSquare, Upload } from "lucide-react";
import React, { useState } from "react";

export const IndexPage: React.FC = () => {
    const [, setChatbot] = useAtom(chatbotOpenAtom);
    const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string; extract_path?: string } | null>(null);
    const [showSnackbar, setShowSnackbar] = useState(false);

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
                    message: "upload failed"
                });
                setShowSnackbar(true);
            }
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
                </div>
            </div>
        </div>
    );
};

export default IndexPage;
