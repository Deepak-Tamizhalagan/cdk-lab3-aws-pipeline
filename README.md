# Lab 3 – AWS CDK Infrastructure + CodePipeline CI/CD Automation

This lab demonstrates automated deployment of AWS infrastructure using **AWS CDK (Python)** and **AWS CodePipeline** integrated with GitHub.

## 🔹 1. Infrastructure Setup (CdkLab3Stack)
- Created CDK project using: `cdk init --language python`
- Defined **Lambda function** with simple JSON return
- Added **API Gateway REST API** with endpoint `GET /hello`
- Linked API to Lambda via proxy integration
- Successfully validated using `cdk synth` and `cdk deploy`

<img width="760" height="217" alt="image" src="https://github.com/user-attachments/assets/da991c76-99d2-4280-a828-d004c80a95f4" />


---

## 🔹 2. GitHub Integration
- Created repo: `cdk-lab3-aws-pipeline`
- Added CodeStar connection to GitHub (status: *Available*)
- Pipeline configured to trigger on pushing to `main` branch

<img width="1038" height="687" alt="image" src="https://github.com/user-attachments/assets/b9bcf1f7-e612-4cbc-a9d4-b7dc394aded8" />


---

## 🔹 3. CI/CD Pipeline (PipelineStack)
- Source Stage: Fetches code from GitHub via CodeStar
- Build Stage: CodeBuild runs:
  ```bash
  npm install -g aws-cdk
  pip install -r requirements.txt
  cdk synth
  ```
  <img width="1890" height="707" alt="image" src="https://github.com/user-attachments/assets/4ed7fa6f-c971-48d5-923b-9a64ff763095" />

## 🔹4. Verification

API tested via Postman → returned "Hello from Lambda via API Gateway!"

Logs observed in CodePipeline & CloudBuild

Manual cdk deploy confirmed working deployment

## 🔹 5. Cleanup

Resources removed using cdk destroy

Confirmed deletion of Lambda, API Gateway, and stacks
<img width="685" height="127" alt="image" src="https://github.com/user-attachments/assets/e0557fd9-cd80-40d6-ac1d-d1c9c6ec4db1" />
<img width="673" height="132" alt="image" src="https://github.com/user-attachments/assets/0e14d42d-5450-4067-827b-7bea5858053a" />


