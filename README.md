# CICD Tool

A robust and modular **Continuous Integration and Continuous Deployment (CI/CD) automation framework** that streamlines the software delivery lifecycle.  
This tool provides developers and DevOps engineers with reliable pipelines for **building, testing, containerizing, and deploying applications** across diverse environments.

---

## Key Features
- **Automated Build Pipelines** – Trigger builds on code commits or pull requests.  
- **Integrated Testing** – Supports unit and integration tests with customizable configurations.  
- **Containerization** – Automated Docker image creation and publishing.  
- **Deployment Automation** – Ready for cloud and on-prem deployments via Kubernetes or Docker Compose.  
- **Configuration-Driven** – Pipeline behavior defined in simple YAML/JSON files.  
- **Team Notifications** – Optional integrations with Slack, Teams, or email.  

---

## Tech Stack
- **Languages:** Python (core scripting), YAML (pipeline definitions)  
- **CI/CD Platform:** GitHub Actions (default) – extensible to Jenkins, GitLab CI  
- **Containerization:** Docker, GitHub Container Registry / Docker Hub  
- **Orchestration:** Kubernetes (with Helm chart support)  
- **Testing Frameworks:** Pytest, Unittest (customizable)  
- **Version Control:** Git / GitHub  

---

## Repository Structure
```
cicd-tool/
│── .github/workflows/   # Predefined GitHub Actions workflows
│── scripts/             # Build, test, deploy automation scripts
│── docker/              # Dockerfiles and Compose configurations
│── docs/                # Technical documentation
│── src/                 # Application source code
│── tests/               # Automated test cases
│── README.md            # Project documentation
```

---

## Getting Started

### Prerequisites
- Git (>= 2.x)  
- Python (>= 3.9)  
- Docker (>= 20.x)  
- Optional: `kubectl` and Helm for Kubernetes deployments  
- GitHub Actions enabled on your repository  

### Installation
Clone the repository:
```bash
git clone https://github.com/amanverma-wsu/cicd-tool.git
cd cicd-tool
```

Set up a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

### Run Pipelines Locally
```bash
python scripts/run_pipeline.py --config config.yaml
```

### Example GitHub Actions Workflow
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ "main" ]

jobs:
  build-test-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Build Application
        run: python scripts/build.py

      - name: Run Tests
        run: pytest tests/

      - name: Build Docker Image
        run: docker build -t cicd-tool:latest .

      - name: Deploy Application
        run: ./scripts/deploy.sh
```

---

## Roadmap
- [ ] Add support for Jenkins and GitLab CI  
- [ ] Expand Kubernetes deployment with Helm charts  
- [ ] Integrate secrets management (HashiCorp Vault, Mozilla SOPS)  
- [ ] Add observability via Prometheus & Grafana  

---

## Contributing
We welcome contributions from the community. To contribute:  
1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/my-feature`)  
3. Commit changes (`git commit -m 'Add feature'`)  
4. Push to your branch (`git push origin feature/my-feature`)  
5. Open a Pull Request  

---

## License
This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.  

---

## Author
**Aman Verma**  
Washington State University  

- [GitHub](https://github.com/amanverma-wsu)  
- [LinkedIn](https://www.linkedin.com/in/aman-verma-alpha/)
