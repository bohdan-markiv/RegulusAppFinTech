import AWS from 'aws-sdk';

// Configure AWS SDK with your credentials and region
AWS.config.update({
    accessKeyId: 'AKIAXYKJVXSDWVWXXAUE',
    secretAccessKey: 'FzljsSDPektvoaPGSGDrKpxNfnMqaoDGL+bl1L9a',
    region: 'eu-cental-1'
});

// Export the configured S3 instance
const s3 = new AWS.S3();

export default s3;
