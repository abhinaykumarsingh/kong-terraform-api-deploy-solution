# 🚀 Kong API Deployment using Terraform + OpenAPI + decK

## 📌 Overview

This project automates the deployment of APIs to Kong Konnect using a **pure Terraform-driven workflow**, with OpenAPI as the source of truth.

It demonstrates how to:

- Convert an OpenAPI specification into Kong configuration using **decK**
- Transform Kong configuration into Terraform resources using a custom Python script
- Deploy services and routes to Kong Konnect using Terraform

> ⚠️ **Note:** Currently, this solution supports only **Services and Routes**.
> Plugin support (e.g., key-auth, rate limiting) is intentionally not included in this version.

---

## 🧱 Architecture

```
OpenAPI Spec (openapi.yaml)
        ↓
decK (openapi2kong)
        ↓
kong.yaml
        ↓
convert.py
        ↓
generated.tf.json
        ↓
Terraform Apply
        ↓
Kong Konnect (Service + Routes)
```

---

## 📁 Project Structure

```
.
├── openapi.yaml          # API definition (source of truth)
├── kong.yaml             # Generated via decK (ignored in git)
├── convert.py            # Converts kong.yaml → Terraform JSON
├── generated.tf.json     # Auto-generated Terraform resources
├── main.tf               # Terraform provider config
├── variables.tf          # Input variables
├── deploy.sh             # End-to-end automation script
├── .gitignore            # Prevents sensitive files from being committed
```

---

## ⚙️ Prerequisites

Make sure the following are installed:

- Terraform (>= 1.0)
- Python (>= 3.8)
- decK CLI
- Kong Konnect account

---

## 🔐 Configuration

Create a `terraform.tfvars` file (DO NOT commit this file):

```hcl
konnect_token     = "your-konnect-token"
control_plane_id  = "your-control-plane-id"
```

---

## 🚀 How to Run

### 1. Validate OpenAPI

Ensure your `openapi.yaml` is valid.

---

### 2. Convert OpenAPI → Kong config

```bash
deck file openapi2kong --spec openapi.yaml --output-file kong.yaml
```

---

### 3. Convert Kong config → Terraform

```bash
python convert.py
```

---

### 4. Deploy using Terraform

```bash
terraform init
terraform validate
terraform apply
```

---

## 🧪 Example

This project includes a sample OpenAPI spec for:

- Backend: `https://httpbin.org`
- Route: `/anything`

After deployment, you can test:

```bash
curl https://<your-kong-url>/anything
```

---

## ⚠️ Limitations

- ❌ Plugins are not supported (yet)
- ❌ Consumers are not managed
- ❌ Secrets are not handled in this pipeline

This is a **minimal, stable foundation** focusing only on:

- Service creation
- Route mapping

---

## 🔮 Future Enhancements

- Add plugin support (key-auth, JWT, rate limiting)
- Secure secret management (Konnect Vault / env vars)
- Consumer automation
- CI/CD integration (GitHub Actions)

---

## 🛡️ Security Notes

- Do NOT commit:
  - `terraform.tfvars`
  - `terraform.tfstate`
  - `.terraform/`

- Use `.gitignore` properly to avoid leaking credentials

---

## 👨‍💻 Author

**Abhinay Kumar Singh**
