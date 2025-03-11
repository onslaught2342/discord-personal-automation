import json
import requests
from datetime import datetime

STATUS_FILE = "status.txt"

def ping_url(url):
    """Check if the URL is reachable."""
    try:
        response = requests.get(url, timeout=5)
        return "🟢 Online" if response.status_code == 200 else "🔴 Offline"
    except requests.RequestException:
        return "🔴 Offline"

def format_timestamp(timestamp):
    """Format timestamp to a readable format."""
    if timestamp == "Unknown":
        return timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return timestamp

def format_status():
    """Format deployment status from JSON files and save to status.txt."""
    message = "**🚀 Project Status Update:**\n"

    # Load Vercel Deployments
    with open("vercel.json") as f:
        vercel_data = json.load(f).get("deployments", [])

    if vercel_data:
        message += "\n**Service: Vercel**"
        # Group deployments by project name
        projects = {}
        for deploy in vercel_data:
            name = deploy.get("name", "Unknown")
            if name not in projects:
                projects[name] = []
            projects[name].append(deploy)

        for name, deployments in projects.items():
            # Sort deployments by created_at timestamp (newest first)
            deployments.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
            latest_deploy = deployments[0]
            url = f"https://{latest_deploy.get('url', 'No URL')}"
            status = latest_deploy.get("state", "Unknown").capitalize()
            ping = ping_url(url)
            message += f"\n  - **Project:** {name}"
            message += f"\n    **Deployed URL:** {url}"
            message += f"\n    **Status of Deployed Site:** {ping}"
            message += f"\n    **Last 10 Deployments:**"
            for i, deploy in enumerate(deployments[:10]):
                created_at = format_timestamp(deploy.get("createdAt", "Unknown"))
                message += f"\n      {i+1}. {created_at}"
            message += "\n    ----------------------------"
    else:
        message += "\n**Service: Vercel**\n  No deployments found"

    # Load Cloudflare Pages Projects
    with open("cloudflare.json") as f:
        cloudflare_data = json.load(f).get("result", [])

    if cloudflare_data:
        message += "\n\n**Service: Cloudflare**"
        for project in cloudflare_data:
            name = project.get("name", "Unknown")
            latest_deployment = project.get("latest_deployment", {})
            url = latest_deployment.get("url", "No URL")
            if not url.startswith("http"):
                url = f"https://{url}"  # Ensure URL is properly formatted
            status = latest_deployment.get("status", "Unknown").capitalize()
            ping = ping_url(url)
            message += f"\n  - **Project:** {name}"
            message += f"\n    **Deployed URL:** {url}"
            message += f"\n    **Status of Deployed Site:** {ping}"
            message += f"\n    **Last 10 Deployments:**"
            deployments = project.get("deployments", [])
            for i, deploy in enumerate(deployments[:10]):
                created_at = format_timestamp(deploy.get("created_on", "Unknown"))
                message += f"\n      {i+1}. {created_at}"
            message += "\n    ----------------------------"
    else:
        message += "\n**Service: Cloudflare**\n  No projects found"

    # Load Netlify Sites
    with open("netlify.json") as f:
        netlify_data = json.load(f)

    if netlify_data:
        message += "\n\n**Service: Netlify**"
        for site in netlify_data:
            name = site.get("name", "Unknown")
            url = site.get("url", "No URL")
            if not url.startswith("http"):
                url = f"https://{url}"  # Ensure URL is properly formatted
            state = site.get("state", "Unknown").capitalize()
            ping = ping_url(url)
            message += f"\n  - **Project:** {name}"
            message += f"\n    **Deployed URL:** {url}"
            message += f"\n    **Status of Deployed Site:** {ping}"
            message += f"\n    **Last 10 Deployments:**"
            deployments = site.get("deployments", [])
            for i, deploy in enumerate(deployments[:10]):
                created_at = format_timestamp(deploy.get("created_at", "Unknown"))
                message += f"\n      {i+1}. {created_at}"
            message += "\n    ----------------------------"
    else:
        message += "\n**Service: Netlify**\n  No sites found"

    # Save to file
    with open(STATUS_FILE, "w", encoding="utf-8") as file:
        file.write(message)

if __name__ == "__main__":
    format_status()