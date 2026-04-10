import yaml
import json
import re
from urllib.parse import urlparse

CONTROL_PLANE_VAR = "${var.control_plane_id}"

def safe_name(name):
    """Convert names into Terraform-safe identifiers"""
    name = name.lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    return name

def parse_url(url):
    """Extract protocol, host, port from URL safely"""
    parsed = urlparse(url)

    protocol = parsed.scheme if parsed.scheme else "https"
    host = parsed.hostname if parsed.hostname else "example.com"

    if parsed.port:
        port = parsed.port
    else:
        port = 443 if protocol == "https" else 80

    return protocol, host, port

# Load kong.yaml
with open("kong.yaml") as f:
    kong = yaml.safe_load(f)

tf = {
    "resource": {
        "konnect_gateway_service": {},
        "konnect_gateway_route": {},
        "konnect_gateway_plugin": {}
    }
}

service_count = 0
route_count = 0
plugin_count = 0

for svc in kong.get("services", []):
    service_count += 1

    svc_name = safe_name(svc["name"]) + f"_{service_count}"

    # ✅ Extract URL properly
    url = svc.get("url", "")
    protocol, host, port = parse_url(url)

    # ✅ SERVICE (correct schema)
    tf["resource"]["konnect_gateway_service"][svc_name] = {
        "name": svc["name"],
        "protocol": protocol,
        "host": host,
        "port": port,
        "control_plane_id": CONTROL_PLANE_VAR
    }

    # ✅ ROUTES (correct linking)
    for route in svc.get("routes", []):
        route_count += 1

        route_name = safe_name(route["name"]) + f"_{route_count}"

        tf["resource"]["konnect_gateway_route"][route_name] = {
            "name": route["name"],
            "paths": route.get("paths", []),
            "methods": route.get("methods", []),
            "service": {
                "id": f"${{konnect_gateway_service.{svc_name}.id}}"
            },
            "control_plane_id": CONTROL_PLANE_VAR
        }


# ✅ Remove empty blocks
tf["resource"] = {k: v for k, v in tf["resource"].items() if v}

# Write Terraform JSON
with open("generated.tf.json", "w") as f:
    json.dump(tf, f, indent=2)

print("✅ generated.tf.json created successfully")