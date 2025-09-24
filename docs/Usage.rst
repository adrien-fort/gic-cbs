Usage
=====

The GIC Cinema Booking System is a command-line application for managing movie seat reservations, bookings, and seat availability.

To run the application:

1. Activate your Python virtual environment (if not already active):

	```
	source venv/bin/activate  # On Linux/macOS
	venv\Scripts\activate    # On Windows
	```

2. Start the booking system:

	```
	python -m src.main
	```


You will be guided through:

- Creating a movie and seating map
- Booking tickets (with best-available or custom seat selection)
- Checking bookings and seat status
- Viewing seat availability

All actions and errors are logged to the `logs/` directory for observability.

Pipeline & AKS Deployment
------------------------

The CI/CD pipeline automatically:

- Runs tests and coverage
- Performs SonarQube static analysis
- Builds Sphinx documentation
- Builds and pushes Docker images to Azure Container Registry (ACR)
- Provisions AKS and ACR in Singapore via Terraform
- Deploys to AKS and runs rollout diagnostics
- Runs OWASP ZAP security scan

Access the deployed app via the AKS service public IP:

.. code-block:: bash

   kubectl get svc gic-cbs --namespace default -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

Visit: http://<AKS_PUBLIC_IP>

Troubleshooting
---------------
- If image pull fails, ensure AKS is attached to the correct ACR:

  .. code-block:: bash

     az aks update -n gic-cbs-aks -g gic-cbs-rg --attach-acr giccbsacrforta20250924

- Diagnostics steps will print pod/node status and logs if rollout hangs.
- For pipeline errors, check workflow logs for details.

Security
--------
OWASP ZAP runs automatically after deployment to scan for vulnerabilities. Results are in the workflow logs.
