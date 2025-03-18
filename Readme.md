# AWS Music Subscription Application

## Overview
A cloud-based music subscription application built with AWS services (EC2, S3, API Gateway, Lambda, and DynamoDB). Users can register, log in, search for music, subscribe to songs, and manage their subscriptions, all through a web interface hosted on Amazon EC2.

## Architecture
This application leverages serverless and cloud infrastructure principles using AWS services:

- **Frontend**: HTML/CSS/JavaScript hosted on EC2 instance
- **Backend**: Lambda functions accessed via API Gateway
- **Authentication**: Custom user login system using DynamoDB
- **Data Storage**: 
  - DynamoDB tables for user data and music metadata
  - S3 Bucket for artist images
- **Cloud Hosting**: EC2 instance with Apache2 web server

## Features
- User registration and authentication
- Music search by title, artist, and year
- Music subscription management
- Artist image display from S3
- Fully responsive web interface

## Technical Components

### 1. AWS DynamoDB Tables
- **login**: Stores user credentials and profile information
  - Attributes: email (primary key), user_name, password
- **music**: Stores music metadata
  - Attributes: title, artist, year, web_url, image_url
- **subscriptions**: Tracks user music subscriptions
  - Attributes: email, title, artist, year, image_url

### 2. AWS S3
- Stores artist images referenced in the music database
- Provides fast, scalable image retrieval

### 3. AWS Lambda Functions
API endpoints implemented as Lambda functions:
- **userAuth**: Handles user login verification
- **userRegister**: Creates new user accounts
- **getMusicData**: Retrieves music based on search parameters
- **subscribeMusic**: Adds music to user's subscription
- **unsubscribeMusic**: Removes music from user's subscription
- **getUserSubscriptions**: Gets all subscribed music for a user

### 4. API Gateway
RESTful API with the following endpoints:
- POST `/login`: Authenticate users
- POST `/register`: Create new accounts
- GET `/music`: Query music data
- POST `/subscribe`: Add music to subscriptions
- DELETE `/unsubscribe`: Remove music from subscriptions
- GET `/subscriptions`: Get user subscriptions

### 5. EC2 Instance
- Hosts the web application on Apache2
- Serves the frontend interface

## Setup Instructions

### Prerequisites
- AWS Account (Free tier eligible)
- AWS CLI installed and configured
- Git
- Python 3.8+
- Node.js 14+ (if using JavaScript for Lambda)

### Deployment Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/aws-music-subscription-app.git
cd aws-music-subscription-app
```

#### 2. Configure AWS CLI
```bash
aws configure
# Enter your AWS credentials when prompted
```

#### 3. Create DynamoDB Tables
```bash
python scripts/create_tables.py
```

#### 4. Load Data into Tables
```bash
python scripts/load_data.py
```

#### 5. Create S3 Bucket and Upload Images
```bash
python scripts/setup_s3.py
```

#### 6. Deploy Lambda Functions
```bash
cd lambda
zip -r ../function.zip .
aws lambda create-function --function-name userAuth --runtime python3.9 --role LabRole --handler user_auth.lambda_handler --zip-file fileb://../function.zip
# Repeat for other functions
```

#### 7. Configure API Gateway
```bash
python scripts/setup_api.py
```

#### 8. Launch EC2 Instance
- Launch Ubuntu Server 20.04 LTS EC2 instance
- Configure security group to allow HTTP/HTTPS traffic
- Connect to instance:
```bash
ssh -i "your-key.pem" ubuntu@your-ec2-public-dns
```

#### 9. Deploy Web Application to EC2
```bash
sudo apt update
sudo apt install -y apache2
cd /var/www/html
sudo rm index.html
sudo git clone https://github.com/yourusername/aws-music-subscription-app.git .
sudo systemctl restart apache2
```

## Configuration
Create a `config.js` file in the web application root directory:

```javascript
const CONFIG = {
  apiEndpoint: 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/',
  region: 'us-east-1',
  s3Bucket: 'your-s3-bucket-name'
};
```

## Usage
1. Access the application through the EC2 instance's public DNS: `http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com/`
2. Register a new account or log in with existing credentials
3. Search for music by title, artist, or year
4. Subscribe to music by clicking the "Subscribe" button
5. Manage subscriptions by removing unwanted music

## Project Structure
```
├── web/                  # Frontend application
│   ├── index.html        # Login page
│   ├── register.html     # Registration page
│   ├── main.html         # Main application page
│   ├── js/               # JavaScript files
│   └── css/              # CSS stylesheets
├── lambda/               # Lambda function code
│   ├── user_auth.py      # User authentication function
│   ├── music_data.py     # Music data retrieval function
│   └── subscriptions.py  # Subscription management functions
├── scripts/              # Deployment and setup scripts
│   ├── create_tables.py  # Creates DynamoDB tables
│   ├── load_data.py      # Loads initial data
│   ├── setup_s3.py       # Configures S3 bucket
│   └── setup_api.py      # Configures API Gateway
├── data/                 # Sample data
│   └── a1.json           # Music metadata
└── README.md             # Project documentation
```

## Security Considerations
- Never hardcode AWS credentials in your application
- Use HTTPS for your API Gateway endpoints
- Implement proper authentication and authorization
- Store passwords securely (hashed and salted)
- Follow AWS security best practices

## Troubleshooting
- **Connection Issues**: Verify security group settings allow HTTP/HTTPS traffic
- **API Errors**: Check CloudWatch logs for Lambda function errors
- **Permission Denied**: Ensure proper IAM role permissions are set
- **Image Not Loading**: Verify S3 bucket policy allows public read access

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- RMIT University COSC2626/2640 Cloud Computing course
- AWS Free Tier for providing resources for development and testing
