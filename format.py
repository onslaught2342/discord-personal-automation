import json
import requests
from datetime import datetime, timezone

STATUS_FILE = "status.txt"

def ping_url(url):
    """Check if the URL is reachable."""
    try:
        response = requests.get(url, timeout=5)
        return "Online" if response.status_code == 200 else "Offline"
    except requests.RequestException:
        return "Offline"


def format_timestamp(timestamp):
    """Format timestamp to a readable format."""
    if timestamp in ["Unknown", None]:
        return "Unknown"
    try:
        if isinstance(timestamp, int):  # Unix timestamp
            return datetime.fromtimestamp(timestamp / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        elif isinstance(timestamp, str):  # ISO format
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, TypeError):
        return "Invalid timestamp"
    return "Unknown"


def format_service(service_name, projects, base_url):
    """Format service output."""
    message = f"\n=== {service_name} ===\n"
    if base_url:
        message += f"\n  🌍 **Base URL:** {base_url}\n"
    for project in projects:
        name = project.get("name", "Unknown")
        url = project.get("url", "No URL")
        status = project.get("status", "Unknown")
        last_deployment = format_timestamp(project.get("last_deployment", "Unknown"))
        ping = ping_url(url)

        message += f"\n  ➤ **Project:** {name}\n"
        message += f"    🔗 **Deployed URL:** {url}\n"
        message += f"    📌 **Status:** {ping}\n"
        message += f"    ⏳ **Last Deployment:** {last_deployment}\n"
    return message


def format_status():
    """Format deployment status from JSON files and save to status.txt."""
    message = "🚀 **Project Status Update** 🚀\n"

    # Load and process Vercel data
    with open("vercel.json") as f:
        vercel_data = json.load(f).get("deployments", [])
    vercel_projects = []
    for project in vercel_data:
        for deploy in project.get("latestDeployments", []):
            vercel_projects.append({
                "name": project.get("name", "Unknown"),
                "url": f"https://{deploy.get('url', 'No URL')}",
                "status": "Online" if deploy.get("readyState") == "READY" else "Offline",
                "last_deployment": deploy.get("createdAt", "Unknown"),
            })
    message += format_service("Vercel", vercel_projects, "https://vercel.com/")

    # Load and process Cloudflare data
    with open("cloudflare.json") as f:
        cloudflare_data = json.load(f).get("result", [])
    cloudflare_projects = [
        {
            "name": project.get("name", "Unknown"),
            "url": project.get("latest_deployment", {}).get("url", "No URL"),
            "status": "Online" if project.get("latest_deployment", {}).get("latest_stage", {}).get("status") == "success" else "Offline",
            "last_deployment": project.get("latest_deployment", {}).get("created_on", "Unknown"),
        }
        for project in cloudflare_data
    ]
    base_url = cloudflare_data[0].get("subdomain", "https://dash.cloudflare.com/") if cloudflare_data else "https://dash.cloudflare.com/"
    message += format_service("Cloudflare", cloudflare_projects, base_url)

    # Load and process Netlify data
    with open("netlify.json") as f:
        netlify_data = json.load(f)
    netlify_projects = [
        {
            "name": site.get("name", "Unknown"),
            "url": site.get("url", "No URL"),
            "status": "Online" if site.get("state") == "current" else "Offline",
            "last_deployment": site.get("published_deploy", {}).get("created_at", "Unknown"),
        }
        for site in netlify_data
    ]
    base_url = netlify_data[0].get("admin_url", "https://app.netlify.com/") if netlify_data else "https://app.netlify.com/"
    message += format_service("Netlify", netlify_projects, base_url)

    # Save to file
    with open(STATUS_FILE, "w", encoding="utf-8") as file:
        file.write(message)

if __name__ == "__main__":
    format_status()
