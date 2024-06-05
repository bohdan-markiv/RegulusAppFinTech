import React, { ChangeEvent } from 'react';
import attachedIcon from './visuals/attached.png';

interface FileUploadProps {
    conversationId: string;
    selectedFile: globalThis.File | null;
    setSelectedFile: React.Dispatch<React.SetStateAction<globalThis.File | null>>;
}

const FileUpload: React.FC<FileUploadProps> = ({ selectedFile, setSelectedFile }) => {

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFile(e.target.files[0]);
        }
    };

    return (
        <div>
            <input
                type="file"
                onChange={handleFileChange}
                id="file-upload"
                style={{ display: 'none' }}
            />
            <label htmlFor="file-upload" style={{ cursor: 'pointer', display: 'inline-block' }}>
                <img src={attachedIcon} alt="Attached" style={{ marginLeft: '10px', width: '40px', height: '40px' }} />
            </label>
            {selectedFile && <p>Selected File: {selectedFile.name}</p>}
        </div>
    );
};

export default FileUpload;
