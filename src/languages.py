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
                lang, {"size": 0, "colour": item["node"]["color"], "language": lang}
            )
            entry["size"] += size
            total += size
            languages[lang] = entry
    for lang in languages.values():
        lang["frac"] = (lang["size"] * 100) / total
    languages = sorted(languages.values(), key=lambda l: l["frac"], reverse=True)


if __name__ == "__main__":
    main()
