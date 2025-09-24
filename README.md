# gic-cbs Project


## Overview
The `gic-cbs` project is a command-line cinema booking system for managing movie seat reservations, bookings, and seat availability. It is designed for demonstration, learning, and testing of robust booking logic, validation, and observability in Python. The project follows a Test-Driven Development (TDD) approach, ensuring all features are thoroughly tested before implementation.

## Installation
To install the necessary dependencies, you can use the following command:

```
pip install -r requirements.txt
```


## Usage
To run the cinema booking system, activate your virtual environment and execute:

```
python -m src.main
```


You will be prompted to create a movie, book tickets, check bookings, and view seat availability through a simple interactive menu. All actions and errors are logged for observability.


## Running Tests
This project uses `pytest` for testing. To run the tests, execute the following command in your Python virtual env:

```
pytest
```

## Observability

As this is a very basic application which doesn't even have API, no advanced telemetry except for logging has been put in place. The code will automatically create a logs directory under the project root and one log file per day will be created. Logs will append to the same file on any given day if the app is restarted.

## Documentation
The documentation for the project is generated using Sphinx. You can build the documentation by navigating to the `docs` directory and running:

```
make html
```

The generated documentation will be available in the `_build/html` directory or as menntioned above the documentation is also auto-generated each time the CI pipeline runs.

## Pipeline & Deployment

This project uses GitHub Actions for CI/CD, deploying to Azure Kubernetes Service (AKS) with a secure, globally unique Azure Container Registry (ACR). The pipeline includes:

- Automated testing and coverage reporting
- SonarQube static analysis
- Sphinx documentation build and artifact upload
- Docker image build and push to ACR
- Terraform provisioning of AKS and ACR in Singapore
- Kubernetes manifest apply and rollout diagnostics
- OWASP ZAP security scan against the deployed service
- Manual rollback job for safe deployment recovery

### AKS Deployment Access
After a successful deploy, access the app via the public IP of the AKS service:

```
kubectl get svc gic-cbs --namespace default -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```
Visit: `http://<AKS_PUBLIC_IP>`

### Troubleshooting
- If image pull fails, ensure AKS is attached to the correct ACR:
  `az aks update -n gic-cbs-aks -g gic-cbs-rg --attach-acr giccbsacrforta20250924`
- If rollout hangs, diagnostics steps will print pod/node status and logs.
- For pipeline errors, check workflow logs for details on each step.

## Security
OWASP ZAP is run automatically after deployment to scan for vulnerabilities. Results will be available in the workflow logs.

## Contribution
Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch to your forked repository.
5. Create a pull request.

## License
This project is licensed under the MIT license. See the LICENSE file for more details.