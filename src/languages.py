import requests
import requests.auth
import os


query = """
query {
    viewer {
        repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
            nodes {
                name
                languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                    edges {
                        size
                        node {
                            color
                            name
                        }
                    }
                }
            }
        }
    }
}
"""


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


def post(query: str):
    token = os.environ["PROFILE_TOKEN"]
    url = "https://api.github.com/graphql"
    response = requests.post(url, json={"query": query}, auth=BearerAuth(token))
    if not response.ok:
        raise Exception(response.content)
    return response.json()


def render_most_used(languages):
    WIDTH = 300
    HEIGHT = 160
    INNER_WIDTH = WIDTH - 30

    style = (
        "    .header {font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: #2f80ed; }\n"
        "    .lang-name {font: 400 11px 'Segoe UI', Ubuntu, Sans-Serif; fill: #888; }\n"
    )

    contents = (
        f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none" role="img" xmlns="http://www.w3.org/2000/svg">\n'
        f"  <style>\n{style}  </style>\n"
        f'  <rect x="0.5" y="0.5" rx="4.5" width="{WIDTH-1}" height="{HEIGHT-1}" stroke="#888" stroke-opacity="1" fill="none" />\n'
        f'  <g transform="translate(15,25)"><text x="0" y="0" class="header">Most Used Languages</text></g>\n'
        f'  <g transform="translate(15,45)">\n'
        f'    <mask id="items-mask"><rect x="0" y="0" width="{INNER_WIDTH}" height="8" rx="5" fill="#fff" /></mask>\n'
    )

    x = 0
    for idx, item in enumerate(languages[:8]):
        width = INNER_WIDTH * item["frac"] / 100
        contents += f'    <rect mask="url(#items-mask)" x="{x:.0f}" y="0" width="{(width+1):.0f}" height="8" fill="{item["color"]}" />\n'
        x += width

        y = (idx // 2) * 20 + 25
        p = (idx % 2) * INNER_WIDTH / 2 + 15
        contents += f'    <g transform="translate({p},{y})">'
        contents += f'<circle cx="5" cy="5" r="5" fill="{item["color"]}" />'
        contents += f'<text x="15" y="10" class="lang-name">{item["language"]} ({item["frac"]:.1f}%)</text>'
        contents += f"</g>\n"
    if x < INNER_WIDTH:
        width = INNER_WIDTH - x
        contents += f'    <rect mask="url(#items-mask)" x="{x:.0f}" y="0" width="{(width+1):.0f}" height="8" fill="#888" />\n'

    contents += "  </g>\n"
    contents += "</svg>\n"

    os.makedirs("images", exist_ok=True)
    with open("images/lang.svg", "w") as f:
        f.write(contents)


def main():
    excluded = [
        "dotfiles",
    ]

    response = post(query)
    if "errors" in response:
        print(response.errors)

    repositories = filter(
        lambda repo: repo["name"] not in excluded,
        response["data"]["viewer"]["repositories"]["nodes"],
    )
    languages = {}
    total = 0
    for repo in repositories:
        for item in repo["languages"]["edges"]:
            lang = item["node"]["name"]
            size = item["size"]
            entry = languages.get(
                lang, {"size": 0, "color": item["node"]["color"], "language": lang}
            )
            entry["size"] += size
            total += size
            languages[lang] = entry
    for lang in languages.values():
        lang["frac"] = (lang["size"] * 100) / total
    languages = sorted(languages.values(), key=lambda l: l["frac"], reverse=True)

    render_most_used(languages)


if __name__ == "__main__":
    main()
