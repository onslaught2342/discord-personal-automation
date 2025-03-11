import json
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

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
            if timestamp > 1000000000000:  # Milliseconds
                timestamp /= 1000
            return datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        elif isinstance(timestamp, str):  # ISO format
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, TypeError, OSError):
        return "Unknown"

def load_json(filename):
    """Load JSON data safely."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def check_status_parallel(projects):
    """Parallelize URL checks for performance."""
    with ThreadPoolExecutor() as executor:
        urls = [proj["url"] for proj in projects if proj["url"] != "No URL"]
        statuses = list(executor.map(ping_url, urls))
    for i, project in enumerate(projects):
        if project["url"] != "No URL":
            project["status"] = statuses[i]

def format_service_summary(service_name, projects, base_url):
    """Format a high-level service summary."""
    message = f"\n=== {service_name} ===\n"
    if base_url:
        message += f"Base URL: {base_url}\n"
    for project in projects:
        name = project.get("name", "Unknown")
        url = project.get("url", "No URL")
        message += f"- {name}: {url}\n"
    return message

def format_deployments(service_name, projects, base_url):
    """Format detailed deployment status."""
    message = format_service_summary(service_name, projects, base_url)
    for project in projects:
        name = project.get("name", "Unknown")
        url = project.get("url", "No URL")
        status = project.get("status", "Unknown")
        last_deployment = format_timestamp(project.get("last_deployment", "Unknown"))
        deployments = project.get("deployments", [])
        
        message += f"  - Project: {name}\n"
        message += f"    Deployed URL: {url}\n"
        message += f"    Status: {status}\n"
        message += f"    Last Deployment: {last_deployment}\n"
        if deployments:
            message += "    Last 10 deployments:\n"
            for deploy in deployments[:10]:
                message += f"      - {format_timestamp(deploy)}\n"
    return message

def format_status():
    """Format deployment status from JSON files and save to status.txt."""
    message = "\U0001F680 **Project Status Update** \U0001F680\n"

    cloudflare_data = load_json("cloudflare.json").get("result", [])
    cloudflare_projects = [
        {
            "name": project.get("name", "Unknown"),
            "url": project.get("subdomain", "No URL"),
            "status": "Unknown",
            "last_deployment": project.get("latest_deployment", {}).get("created_on", "Unknown"),
            "deployments": [project.get("latest_deployment", {}).get("created_on")]
        }
        for project in cloudflare_data
    ]
    
    netlify_data = load_json("netlify.json")
    netlify_projects = [
        {
            "name": site.get("name", "Unknown"),
            "url": site.get("ssl_url", "No URL"),
            "status": "Unknown",
            "last_deployment": site.get("published_deploy", {}).get("created_at", "Unknown"),
            "deployments": [deploy.get("created_at") for deploy in site.get("deploys", [])][:10]
        }
        for site in netlify_data
    ]
    
    vercel_data = load_json("vercel.json").get("projects", [])
    vercel_projects = [
        {
            "name": project.get("name", "Unknown"),
            "url": next((alias for alias in project.get("latestDeployments", [{}])[0].get("alias", []) if "vercel.app" in alias), "No URL"),
            "status": "Unknown",
            "last_deployment": project.get("latestDeployments", [{}])[0].get("createdAt", "Unknown"),
            "deployments": [deploy.get("createdAt") for deploy in project.get("latestDeployments", [])]
        }
        for project in vercel_data
    ]

    check_status_parallel(cloudflare_projects)
    check_status_parallel(netlify_projects)
    check_status_parallel(vercel_projects)

    message += format_deployments("Cloudflare", cloudflare_projects, "https://dash.cloudflare.com/")
    message += format_deployments("Netlify", netlify_projects, "https://app.netlify.com/")
    message += format_deployments("Vercel", vercel_projects, "https://vercel.com/")

    with open(STATUS_FILE, "w", encoding="utf-8") as file:
        file.write(message)

if __name__ == "__main__":
    format_status()