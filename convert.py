import yaml
import json
import re

CONTROL_PLANE_VAR = "${var.control_plane_id}"

# =========================================================
# SAFE NAME
# =========================================================
def safe_name(name):
    if not name:
        raise ValueError("❌ Name is missing")

    name = name.lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    return name


# =========================================================
# LOAD YAML
# =========================================================
with open("kong.yaml") as f:
    kong = yaml.safe_load(f)

if not kong:
    raise ValueError("❌ YAML file is empty or invalid")


# =========================================================
# INIT TF STRUCTURE
# =========================================================
tf = {
    "resource": {
        "konnect_gateway_service": {},
        "konnect_gateway_route": {},
        "konnect_gateway_plugin_key_auth": {},
        "konnect_gateway_plugin_rate_limiting": {}
    }
}

service_count = 0
route_count = 0


# =========================================================
# DETECT KONG FORMAT
# =========================================================
if "services" in kong:
    print("🔍 Detected Kong format")

    for svc in kong.get("services", []):
        service_count += 1

        svc_name_raw = svc.get("name")
        if not svc_name_raw:
            raise ValueError("❌ Service name missing")

        svc_name = safe_name(svc_name_raw) + f"_{service_count}"

        # =====================================================
        # FIX: USE DIRECT FIELDS FROM DECK OUTPUT
        # =====================================================
        protocol = svc.get("protocol")
        host = svc.get("host")
        port = svc.get("port")

        if not protocol or not host or not port:
            raise ValueError(
                f"❌ Incomplete service definition for {svc_name_raw} "
                f"(protocol/host/port missing)"
            )

        # SERVICE
        tf["resource"]["konnect_gateway_service"][svc_name] = {
            "name": svc_name_raw,
            "protocol": protocol,
            "host": host,
            "port": port,
            "path": "/",
            "control_plane_id": CONTROL_PLANE_VAR
        }

        # =====================================================
        # PLUGINS (KEY AUTH)
        # =====================================================
        tf["resource"]["konnect_gateway_plugin_key_auth"][f"{svc_name}_keyauth"] = {
            "control_plane_id": CONTROL_PLANE_VAR,
            "service": {
                "id": f"${{konnect_gateway_service.{svc_name}.id}}"
            },
            "config": {
                "key_names": ["apikey"]
            }
        }

        # =====================================================
        # PLUGINS (RATE LIMIT)
        # =====================================================
        tf["resource"]["konnect_gateway_plugin_rate_limiting"][f"{svc_name}_ratelimit"] = {
            "control_plane_id": CONTROL_PLANE_VAR,
            "service": {
                "id": f"${{konnect_gateway_service.{svc_name}.id}}"
            },
            "config": {
                "minute": 5,
                "policy": "local"
            }
        }

        # =====================================================
        # ROUTES
        # =====================================================
        for route in svc.get("routes", []):
            route_count += 1

            route_name_raw = route.get("name")
            if not route_name_raw:
                raise ValueError(f"❌ Route name missing in service {svc_name_raw}")

            route_name = safe_name(route_name_raw) + f"_{route_count}"

            tf["resource"]["konnect_gateway_route"][route_name] = {
                "name": route_name_raw,
                "paths": route.get("paths"),
                "methods": route.get("methods"),
                "service": {
                    "id": f"${{konnect_gateway_service.{svc_name}.id}}"
                },
                "control_plane_id": CONTROL_PLANE_VAR
            }

else:
    raise ValueError("❌ Unsupported YAML format (missing services)")


# =========================================================
# CLEANUP EMPTY RESOURCES
# =========================================================
tf["resource"] = {k: v for k, v in tf["resource"].items() if v}


# =========================================================
# WRITE OUTPUT
# =========================================================
with open("generated.tf.json", "w") as f:
    json.dump(tf, f, indent=2)

print("✅ Terraform JSON generated successfully")