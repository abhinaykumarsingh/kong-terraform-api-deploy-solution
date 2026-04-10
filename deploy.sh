#!/usr/bin/env bash

set -euo pipefail

# -----------------------------
# CONFIG
# -----------------------------
OPENAPI_FILE="openapi.yaml"
KONG_FILE="kong.yaml"
TF_JSON_FILE="generated.tf.json"

# -----------------------------
# LOGGING
# -----------------------------
log() {
  echo -e "\n[INFO] $1"
}

error() {
  echo -e "\n[ERROR] $1" >&2
  exit 1
}

# -----------------------------
# CHECK DEPENDENCIES
# -----------------------------
check_dependencies() {
  log "Checking dependencies..."

  command -v deck >/dev/null 2>&1 || error "decK is not installed"
  command -v python >/dev/null 2>&1 || error "Python is not installed"
  command -v terraform >/dev/null 2>&1 || error "Terraform is not installed"

  log "All dependencies are available ✅"
}

# -----------------------------
# VALIDATE INPUT FILE
# -----------------------------
validate_openapi() {
  log "Validating OpenAPI file..."

  [[ -f "$OPENAPI_FILE" ]] || error "Missing $OPENAPI_FILE"

  log "OpenAPI file found ✅"
}

# -----------------------------
# STEP 1: OpenAPI → Kong
# -----------------------------
convert_openapi_to_kong() {
  log "Converting OpenAPI → Kong config..."

  if deck file openapi2kong --help | grep -q -- "--output-file"; then
    deck file openapi2kong --spec "$OPENAPI_FILE" --output-file "$KONG_FILE" || error "decK conversion failed"
  elif deck file openapi2kong --help | grep -q -- "--output"; then
    deck file openapi2kong --spec "$OPENAPI_FILE" --output "$KONG_FILE" || error "decK conversion failed"
  else
    deck file openapi2kong --spec "$OPENAPI_FILE" > "$KONG_FILE" || error "decK conversion failed"
  fi

  [[ -f "$KONG_FILE" ]] || error "kong.yaml not generated"

  log "Kong config generated ✅"
}

# -----------------------------
# STEP 2: Kong → Terraform JSON
# -----------------------------
convert_kong_to_tf() {
  log "Converting Kong → Terraform JSON..."

  .venv/Scripts/python.exe convert.py || error "Python conversion failed"

  [[ -f "$TF_JSON_FILE" ]] || error "Terraform JSON not generated"

  log "Terraform JSON generated ✅"
}

# -----------------------------
# STEP 3: Terraform Init
# -----------------------------
terraform_init() {
  log "Running terraform init..."

  terraform init -input=false || error "Terraform init failed"
}

# -----------------------------
# STEP 4: Terraform Validate
# -----------------------------
terraform_validate() {
  log "Validating Terraform..."

  terraform validate || error "Terraform validation failed"
}

# -----------------------------
# STEP 5: Terraform Plan
# -----------------------------
terraform_plan() {
  log "Running terraform plan..."

  terraform plan -out=tfplan || error "Terraform plan failed"
}

# -----------------------------
# STEP 6: Terraform Apply
# -----------------------------
terraform_apply() {
  log "Applying Terraform..."

  terraform apply -auto-approve tfplan || error "Terraform apply failed"
}

# -----------------------------
# MAIN EXECUTION
# -----------------------------
main() {
  log "🚀 Starting deployment pipeline..."

  check_dependencies
  validate_openapi
  convert_openapi_to_kong
  convert_kong_to_tf
  terraform_init
  terraform_validate
  terraform_plan
  terraform_apply

  log "🎉 Deployment completed successfully!"
}

main