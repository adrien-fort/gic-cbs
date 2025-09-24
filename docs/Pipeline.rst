Pipeline
========

The CI/CD pipeline for the GIC Cinema Booking System automates testing, analysis, build, deployment, and security scanning using GitHub Actions and Azure services.

Steps:
------

1. **Run Pytest & Coverage**
   - Executes all unit tests and generates a coverage report.
   - Uploads coverage as an artifact for later use.

2. **SonarQube Static Analysis**
   - Downloads coverage report.
   - Runs SonarQube scan for code quality and security.
   - Enforces quality gate.

3. **Build Sphinx Documentation**
   - Builds HTML docs from Sphinx sources.
   - Uploads docs as an artifact.

4. **Build & Save Docker Image**
   - Builds Docker image for the app.
   - Saves and uploads the image as an artifact.

5. **Terraform Apply**
   - Provisions AKS and ACR in Singapore.
   - Imports existing resources if needed.
   - Applies infrastructure changes.

6. **Deploy to AKS**
   - Loads Docker image and pushes to ACR.
   - Updates Kubernetes manifest with correct image tag and ACR login server.
   - Applies manifest and waits for rollout.
   - Runs diagnostics if rollout fails (pod/node status, logs).

7. **OWASP ZAP Security Scan**
   - Work in progress, still need fixing. 
   - Retrieves AKS service public IP.
   - Runs OWASP ZAP against the deployed app for vulnerability scanning.

8. **Manual Rollback Job**
   - Allows safe rollback of AKS deployment if needed.

Accessing the App:
------------------
After deployment, access the app via the AKS service public IP:

.. code-block:: bash

   kubectl get svc gic-cbs --namespace default -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

Visit: http://<AKS_PUBLIC_IP>

Troubleshooting:
----------------
- If image pull fails, attach ACR to AKS:

  .. code-block:: bash

     az aks update -n gic-cbs-aks -g gic-cbs-rg --attach-acr giccbsacrforta20250924

- Diagnostics steps print pod/node status and logs if rollout hangs.
- Check workflow logs for step-by-step details.

Security:
---------
OWASP ZAP runs automatically after deployment. Results are in the workflow logs.
