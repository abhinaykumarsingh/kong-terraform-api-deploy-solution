resource "konnect_gateway_consumer" "app1" {
  username         = "app1"
  custom_id      = "test_user"
  control_plane_id = var.control_plane_id
}

resource "konnect_gateway_key_auth" "app1_key" {
  key              = var.app1_api_key
  consumer_id      = konnect_gateway_consumer.app1.id
  control_plane_id = var.control_plane_id
}

