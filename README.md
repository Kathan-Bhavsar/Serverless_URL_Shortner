# 🔗 Serverless URL Shortener

This is a serverless URL shortener application built using **AWS Lambda**, **API Gateway**, and **S3**. It allows users to shorten long URLs and access the original URLs via generated short codes. All mappings are stored in a central JSON file within S3.

## 🚀 Features

- Generate short URLs from long URLs via a `POST` request.
- Redirect to original URLs using a `GET` request with the short code.
- Fully serverless architecture – no traditional server hosting required.
- Mappings are persisted in an S3 bucket in `urls.json`.

## 🛠️ Technologies Used

- **AWS Lambda** – backend logic execution
- **Amazon API Gateway** – handles HTTP requests
- **Amazon S3** – stores short URL mappings
- **IAM** – secure access control
- **Python (Boto3)** – Lambda function code

