import { chatbotOpenAtom } from "$lib/features/chatbot/atoms";
import { Button, Divider } from "@mui/joy";
import { useAtom } from "jotai";
import { Bot, Box, MessageSquare, Upload } from "lucide-react";
import React from "react";

export const IndexPage: React.FC = () => {
    const [, setChatbot] = useAtom(chatbotOpenAtom);

    const handleZipUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file && file.type === "application/zip") {
            // 处理zip文件上传逻辑
            console.log("Zip file selected:", file.name);
        }
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
            </div>
        </div>
    );
};

export default IndexPage;
