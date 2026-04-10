terraform {
  required_providers {
    konnect = {
      source  = "kong/konnect"
      version = "~> 3.13.0"
    }
  }
}

provider "konnect" {
  server_url            = "https://in.api.konghq.com"
  personal_access_token = var.konnect_token
}