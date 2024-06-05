import AWS from 'aws-sdk';
import axios from 'axios';

interface Message {
    text: string;
    sender: string;
    timestamp: string;
    hasAttachment?: boolean;
}
// Define the Secret interface
interface Conversation {
    id: string;
    text: Message[];
    user_id: string;
    title: string;
    accessKeyId: string;
    secretAccessKey: string;

}
async function configureS3(id: string | undefined) {
    try {
        // Make the GET request to fetch the secret
        const response = await axios.get<Conversation>(`https://vjwir58s9d.execute-api.eu-central-1.amazonaws.com/prod/conversations/${id}`);
        const secret: Conversation = response.data;
        console.log(secret);

        // Update AWS SDK configuration
        AWS.config.update({
            accessKeyId: secret.accessKeyId,
            secretAccessKey: secret.secretAccessKey,
            region: 'eu-central-1'
        });

        // Create and export the configured S3 instance
        const s3 = new AWS.S3();
        return s3;
    } catch (error) {
        console.error('Error configuring AWS SDK:', error);
        throw error;
    }
}

export default configureS3;
