import json
import requests

STATUS_FILE = "status.txt"

def ping_url(url):
    """Check if the URL is reachable."""
    try:
        response = requests.get(url, timeout=5)
        return "🟢 Online" if response.status_code == 200 else "🔴 Offline"
    except requests.RequestException:
        return "🔴 Offline"

def format_status():
    """Format deployment status from JSON files and save to status.txt."""
    message = "**🚀 Project Status Update:**\n"

    # Load Vercel Deployments
    with open("vercel.json") as f:
        vercel_data = json.load(f).get("deployments", [])
    
    if vercel_data:
        message += "\n- **Vercel Deployments:**"
        for deploy in vercel_data:
            name = deploy.get("name", "Unknown")
            url = f"https://{deploy.get('url', 'No URL')}"
            status = deploy.get("state", "Unknown").capitalize()
            ping = ping_url(url)
            message += f"\n  - **Project:** {name}\n    **Status:** {status}\n    **Latest Deploy URL:** {url}\n    **Ping Status:** {ping}"
    else:
        message += "\n- **Vercel Deployments:** No deployments found"

    # Load Cloudflare Pages Projects
    with open("cloudflare.json") as f:
        cloudflare_data = json.load(f).get("result", [])

    if cloudflare_data:
        message += "\n\n- **Cloudflare Pages Projects:**"
        for project in cloudflare_data:
            name = project.get("name", "Unknown")
            latest_deployment = project.get("latest_deployment", {})
            status = latest_deployment.get("status", "Unknown").capitalize()
            last_deployed = latest_deployment.get("created_on", "Unknown")
            message += f"\n  - **Project:** {name}\n    **Status:** {status}\n    **Last Deployed:** {last_deployed}"
    else:
        message += "\n- **Cloudflare Pages Projects:** No projects found"

    # Load Netlify Sites
    with open("netlify.json") as f:
        netlify_data = json.load(f)

    if netlify_data:
        message += "\n\n- **Netlify Sites:**"
        for site in netlify_data:
            name = site.get("name", "Unknown")
            state = site.get("state", "Unknown").capitalize()
            url = site.get("url", "No URL")
            if not url.startswith("http://") and not url.startswith("https://"):
                url = f"https://{url}"  # Ensure URL is properly formatted
            last_published = site.get("published_at", site.get("updated_at", "Unknown"))
            ping = ping_url(url)
            message += f"\n  - **Site:** {name}\n    **State:** {state}\n    **Latest Deploy URL:** {url}\n    **Last Published:** {last_published}\n    **Ping Status:** {ping}"
    else:
        message += "\n- **Netlify Sites:** No sites found"

    # Save to file
    with open(STATUS_FILE, "w", encoding="utf-8") as file:
        file.write(message)

if __name__ == "__main__":
    format_status()