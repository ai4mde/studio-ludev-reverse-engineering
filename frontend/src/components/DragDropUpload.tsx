import { Button, Divider, FormControl, FormLabel, Modal, ModalClose, ModalDialog, Switch, Typography } from '@mui/joy';
import { FileIcon, FolderIcon, Settings, Upload } from 'lucide-react';
import React, { useCallback, useState } from 'react';

interface DragDropUploadProps {
    open: boolean;
    onClose: () => void;
    onFileUpload: (files: FileList, includeMethodDependency: boolean) => void;
    uploadType: 'zip' | 'folder';
    title: string;
    initialMethodDependency?: boolean;
}

export const DragDropUpload: React.FC<DragDropUploadProps> = ({
    open,
    onClose,
    onFileUpload,
    uploadType,
    title,
    initialMethodDependency = true
}) => {
    const [isDragActive, setIsDragActive] = useState(false);
    const [dragCounter, setDragCounter] = useState(0);
    const [includeMethodDependency, setIncludeMethodDependency] = useState(initialMethodDependency);

    const onDragEnter = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragCounter(prev => prev + 1);
        if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
            setIsDragActive(true);
        }
    }, []);

    const onDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragCounter(prev => prev - 1);
        if (dragCounter === 1) {
            setIsDragActive(false);
        }
    }, [dragCounter]);

    const onDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(false);
        setDragCounter(0);

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            onFileUpload(e.dataTransfer.files, includeMethodDependency);
            onClose();
        }
    }, [onFileUpload, onClose, includeMethodDependency]);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            onFileUpload(e.target.files, includeMethodDependency);
            onClose();
        }
    }, [onFileUpload, onClose, includeMethodDependency]);

    const inputProps = uploadType === 'folder'
        ? { webkitdirectory: "true" as any, directory: "true" as any, multiple: true }
        : { accept: ".zip" };

    return (
        <Modal open={open} onClose={onClose}>
            <ModalDialog
                variant="outlined"
                size="lg"
                sx={{
                    width: '500px',
                    maxWidth: '90vw'
                }}
            >
                <ModalClose />
                <Typography level="h4" component="h2" className="mb-4">
                    {title}
                </Typography>

                {/* Method Dependency Settings */}
                <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded-md">
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
                </div>

                <Divider className="mb-4" />

                <div
                    className={`
            border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
            ${isDragActive
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-300 hover:border-gray-400'
                        }
          `}
                    onDragEnter={onDragEnter}
                    onDragLeave={onDragLeave}
                    onDragOver={onDragOver}
                    onDrop={onDrop}
                >
                    <div className="flex flex-col items-center space-y-4">
                        {uploadType === 'zip' ? (
                            <FileIcon size={48} className="text-gray-400" />
                        ) : (
                            <FolderIcon size={48} className="text-gray-400" />
                        )}

                        <div>
                            <Typography level="body-lg" className="font-medium">
                                {isDragActive
                                    ? `Drop your ${uploadType === 'zip' ? 'ZIP file' : 'folder'} here`
                                    : `Drag and drop your ${uploadType === 'zip' ? 'ZIP file' : 'Django project folder'} here`
                                }
                            </Typography>
                            <Typography level="body-sm" className="text-gray-500 mt-1">
                                or click the button below to browse
                            </Typography>
                        </div>

                        <Button
                            component="label"
                            variant="outlined"
                            startDecorator={<Upload size={16} />}
                        >
                            Browse {uploadType === 'zip' ? 'ZIP File' : 'Folder'}
                            <input
                                type="file"
                                hidden
                                onChange={handleFileSelect}
                                {...inputProps}
                            />
                        </Button>
                    </div>
                </div>

                <Typography level="body-sm" className="text-gray-600 mt-4">
                    {uploadType === 'zip'
                        ? 'Select a ZIP file containing your Django project'
                        : 'Select a folder containing your Django project files'
                    }
                </Typography>
            </ModalDialog>
        </Modal>
    );
}; 