import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import logo from './visuals/general_logo.png';

interface Conversation {
    id: string;
    title: string;
}

const ConversationsList: React.FC = () => {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchConversations = async () => {
            try {
                const response = await axios.get<Conversation[]>(`https://vjwir58s9d.execute-api.eu-central-1.amazonaws.com/prod/conversations`);
                setConversations(response.data);
            } catch (error) {
                console.error("Error fetching conversations:", error);
            }
        };

        fetchConversations();
    }, []);

    const handleConversationClick = (id: string) => {
        navigate(`/conversation/${id}`);
    };

    const handleNewConversationClick = async () => {
        try {
            const response = await axios.post<string>(`https://vjwir58s9d.execute-api.eu-central-1.amazonaws.com/prod/conversations`);
            const newConversationId = response.data;
            navigate(`/conversation/${newConversationId}`);
        } catch (error) {
            console.error("Error starting new conversation:", error);
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '20px', fontSize: '22px', marginBottom: '50px' }}>
            <h1>Choose the conversation with Regulus AI</h1>
            <img src={logo} alt="Logo" style={{ width: '450px', height: '300px', marginBottom: '20px' }} />
            <table style={{ borderCollapse: 'collapse', width: '80%', marginTop: '20px', margin: '0 auto', borderRadius: '15px', overflow: 'hidden' }}>
                <thead>
                    <tr>
                        <th style={{ border: '3px solid black', padding: '10px', fontSize: '28px', backgroundColor: '#f2f2f2' }}>Available Chats</th>
                    </tr>
                </thead>
                <tbody>
                    {conversations.map((conversation) => (
                        <tr key={conversation.id}>
                            <td style={{ border: '3px solid black', padding: '10px' }}>
                                <button
                                    onClick={() => handleConversationClick(conversation.id)}
                                    style={{
                                        width: '100%',
                                        background: 'none',
                                        border: 'none',
                                        textAlign: 'left',
                                        padding: '10px',
                                        fontSize: '18px',
                                        cursor: 'pointer',
                                        color: '#333',
                                        transition: 'background-color 0.3s ease',
                                        borderRadius: '15px'
                                    }}
                                    onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#f9f9f9')}
                                    onMouseOut={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                                >
                                    {conversation.title}
                                </button>
                            </td>
                        </tr>
                    ))}
                    <tr>
                        <td style={{ border: '3px solid black', padding: '10px', textAlign: 'center' }}>
                            <button
                                onClick={handleNewConversationClick}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    padding: '10px',
                                    backgroundColor: '#57AF3E',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '5px',
                                    cursor: 'pointer',
                                    fontSize: '15px',
                                    transition: 'background-color 0.3s ease'
                                }}
                                onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#45a32e')}
                                onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#57AF3E')}
                            >
                                Start New Conversation
                                <span style={{ marginLeft: '10px', fontSize: '20px' }}>+</span>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    );
};

export default ConversationsList;
