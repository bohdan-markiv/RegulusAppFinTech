import React, { useState, useEffect, useRef, KeyboardEvent } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import logo from './visuals/logo_with_text.png';
import loadingGif from './visuals/loading.gif';
import attachedIcon from './visuals/attached.png';
import FileUpload from './fileUpload';
import configureS3 from './aws-config';

interface Message {
    text: string;
    sender: string;
    timestamp: string;
    hasAttachment?: boolean;
}

interface Conversation {
    id: string;
    text: Message[];
    user_id: string;
    title: string;
}

interface CustomFile {
    id: string;
    name: string;
}

const DialoguePage: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [newMessage, setNewMessage] = useState<string>('');
    const [selectedFile, setSelectedFile] = useState<globalThis.File | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const navigate = useNavigate();
    const { id } = useParams<{ id: string }>();
    const [chatTitle, setChatTitle] = useState<string>('');

    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchConversation = async () => {

            // This hook is run when the dialogue page is loaded. It takes all the messages from the conversation
            // and set up the chat name.
            try {
                const response = await axios.get<Conversation>(`https://vjwir58s9d.execute-api.eu-central-1.amazonaws.com/prod/conversations/${id}`);
                const sortedMessages = response.data.text.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
                setMessages(sortedMessages);
                setChatTitle(response.data.title);
            } catch (error) {
                console.error("Error fetching conversation:", error);
            }
        };

        fetchConversation();
    }, [id]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSendMessage = async (message: string, file: globalThis.File | null) => {
        if (message.trim() || file) {
            const userMessage: Message = {
                text: message,
                sender: 'user',
                timestamp: new Date().toISOString(),
                hasAttachment: !!file
            };

            // Update messages with user message
            setMessages(prevMessages => [...prevMessages, userMessage]);

            setLoading(true);

            try {
                // Log the data being sent
                console.log('Sending message:', message);
                console.log('Sending file:', file);

                let fileData: CustomFile = { id: '', name: '' };
                if (file) {
                    fileData = await uploadFile(file);
                }

                // Send the message to the API
                const response = await axios.post<string>(
                    `https://vjwir58s9d.execute-api.eu-central-1.amazonaws.com/prod/conversations/${id}/message`,
                    {
                        message,
                        file: fileData
                    }
                );

                // Create bot message with the response text
                const botMessage: Message = {
                    text: response.data,
                    sender: 'bot',
                    timestamp: new Date().toISOString(),
                };

                // Update messages with bot message
                setMessages(prevMessages => [...prevMessages, botMessage]);

            } catch (error) {
                console.error("Error sending message:", error);
            } finally {
                setLoading(false);  // Stop loading
            }

            // Clear the input
            setNewMessage('');
            setSelectedFile(null);
        }
    };

    const uploadFile = async (file: globalThis.File): Promise<CustomFile> => {

        // This hook is sends the selected file to aws s3, and after that uploads it to the OpenAI storage.
        const params = {
            Bucket: 'conversations-admin',
            Key: file.name,
            Body: file,
            ContentType: file.type
        };

        try {
            const s3 = await configureS3(id);
            await s3.upload(params).promise();

            // Send the file name to the API
            const response = await axios.post(
                `https://vjwir58s9d.execute-api.eu-central-1.amazonaws.com/prod/conversations/${id}/file`,
                { filename: file.name }
            );

            return response.data;

        } catch (error) {
            console.error('Error uploading file:', error);
            throw error;
        }
    };

    const handleSendMessageButton = () => {
        handleSendMessage(newMessage, selectedFile).catch(error => console.error(error));
        setNewMessage(''); // Clear the input field immediately
    };

    const handleBackClick = () => {

        // This is a navigation button.
        navigate('/');
    };

    const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {

        // This functionality allows for a custom chat title.
        setChatTitle(e.target.value);
    };

    const handleTitleBlur = async () => {
        try {
            // API call to update the conversation title
            await axios.post(`https://vjwir58s9d.execute-api.eu-central-1.amazonaws.com/prod/conversations/${id}`,
                { title: chatTitle });
            console.log('Title updated');
            console.log(chatTitle);
        } catch (error) {
            console.error("Error updating title:", error);
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {

        // This hook allows to send message just by pressing enter.
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent the default action of adding a new line
            handleSendMessageButton();
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative'
        }}>
            <img
                src={logo}
                alt="Logo"
                style={{
                    position: 'fixed',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '700px',  // Adjust the size as needed
                    height: 'auto',
                    opacity: 0.7, // Optional: make it semi-transparent for better readability of text
                    zIndex: -1
                }}
            />
            <button
                onClick={handleBackClick}
                style={{
                    position: 'fixed',
                    top: '10px',
                    left: '10px',
                    padding: '10px 20px',
                    borderRadius: '5px',
                    border: 'none',
                    backgroundColor: '#57AF3E',
                    color: 'white',
                    zIndex: 1000,
                    fontSize: '18px'
                }}
            >
                Back
            </button>
            <input
                type="text"
                value={chatTitle}
                onChange={handleTitleChange}
                onBlur={handleTitleBlur}
                style={{
                    textAlign: 'center',
                    marginTop: '20px',
                    fontSize: '24px',
                    border: 'none',
                    borderBottom: '1px solid #ddd',
                    outline: 'none',
                    width: '500px',
                    alignSelf: 'center'
                }}
            />
            <div style={{ display: 'flex', flexDirection: 'column', padding: '20px', paddingBottom: '140px' }}>
                {messages.map((message, index) => (
                    <div key={index} style={{
                        display: 'flex',
                        justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                        margin: '10px 0',
                    }}>
                        <div style={{
                            backgroundColor: message.sender === 'user' ? '#DCF8C6' : '#E6E6E6',
                            padding: '10px',
                            borderRadius: '10px',
                            maxWidth: '60%',
                            wordWrap: 'break-word',
                            marginRight: message.sender === 'user' ? '10px' : 'initial',
                            fontSize: '18px',
                        }}>
                            <p>{message.text}</p>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <span style={{ fontSize: '0.8em', color: '#999' }}>{new Date(message.timestamp).toLocaleString()}</span>
                                {message.hasAttachment && <img src={attachedIcon} alt="Attached" style={{ marginLeft: '10px', width: '20px', height: '20px' }} />}
                            </div>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div style={{ display: 'flex', justifyContent: 'flex-start', margin: '20px 0', paddingLeft: '10px' }}>
                        <img src={loadingGif} alt="Loading" width="100" height="100" />
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <div style={{ position: 'fixed', borderTop: '1px solid #ddd', bottom: '0', left: 0, right: 0, backgroundColor: 'white', padding: '10px 0', paddingBottom: '50px', zIndex: 1000 }}>
                <div style={{ display: 'flex', padding: '10px', maxWidth: '100%', backgroundColor: 'white' }}>
                    <textarea
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        style={{
                            flex: 1,
                            padding: '10px',
                            borderRadius: '5px',
                            border: '1px solid #ddd',
                            marginRight: '10px',
                            fontSize: '18px',
                            minHeight: '50px', // You can adjust the minimum height as needed
                            resize: 'vertical' // Allow vertical resizing
                        }}
                        placeholder="Type your message..."
                    />
                    <button onClick={handleSendMessageButton} style={{ padding: '10px 40px', borderRadius: '7px', border: 'none', backgroundColor: '#57AF3E', color: 'white', fontSize: '18px', cursor: 'pointer' }}>
                        Send
                    </button>
                    <FileUpload conversationId={id!} selectedFile={selectedFile} setSelectedFile={setSelectedFile} />
                </div>
            </div>
        </div>
    );
};

export default DialoguePage;
