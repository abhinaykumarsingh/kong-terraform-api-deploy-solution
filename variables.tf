variable "konnect_token" {
  type      = string
  sensitive = true
}

variable "control_plane_id" {
  type = string
}

variable "app1_api_key" {
  description = "API key for app1"
  type        = string
  sensitive   = true
}