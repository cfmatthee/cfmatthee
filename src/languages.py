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
    response = post(query)


if __name__ == "__main__":
    main()
