import datetime as dt
import pandas as pd
import requests
import requests.auth
import os


QUERY = """
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

WIDTH = 300
INNER_WIDTH = WIDTH - 30
HEIGHT = 160
NUM_LANGUAGES = 6

STYLE = (
    "    .header {font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: #2f80ed; }\n"
    "    .lang-name {font: 400 11px 'Segoe UI', Ubuntu, Sans-Serif; fill: #888; }\n"
)


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


def extract_languages(repositories, excluded):
    languages = {}
    total = 0
    for repo in repositories:
        for item in repo["languages"]["edges"]:
            name = repo["name"]
            lang = item["node"]["name"]
            size = item["size"]
            if (
                f"{name}:*" in excluded
                or f"*:{lang}" in excluded
                or f"{name}:{lang}" in excluded
            ):
                continue
            # print(f"found {name}:{lang}")
            entry = languages.get(
                lang, {"size": 0, "color": item["node"]["color"], "language": lang}
            )
            entry["size"] += size
            total += size
            languages[lang] = entry
    for lang in languages.values():
        lang["frac"] = (lang["size"] * 100) / total
    languages = sorted(languages.values(), key=lambda l: l["frac"], reverse=True)
    return languages


def render_most_used(languages):
    contents = (
        f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none" role="img" xmlns="http://www.w3.org/2000/svg">\n'
        f"  <style>\n{STYLE}  </style>\n"
        f'  <rect x="0.5" y="0.5" rx="4.5" width="{WIDTH-1}" height="{HEIGHT-1}" stroke="#888" stroke-opacity="1" fill="none" />\n'
        f'  <g transform="translate(15,25)"><text x="0" y="0" class="header">Most Used Languages</text></g>\n'
        f'  <g transform="translate(15,45)">\n'
        f'    <mask id="lang-mask"><rect x="0" y="0" width="{INNER_WIDTH}" height="8" rx="5" fill="#fff" /></mask>\n'
    )

    x = 0
    for idx, item in enumerate(languages[:NUM_LANGUAGES]):
        width = INNER_WIDTH * item["frac"] / 100
        contents += f'    <rect mask="url(#lang-mask)" x="{x:.0f}" y="0" width="{(width+1):.0f}" height="8" fill="{item["color"]}" />\n'
        x += width

        y = (idx // 2) * 20 + 40
        p = (idx % 2) * INNER_WIDTH / 2 + 15
        contents += f'    <g transform="translate({p},{y})">'
        contents += f'<circle cx="5" cy="5" r="5" fill="{item["color"]}" />'
        contents += f'<text x="15" y="10" class="lang-name">{item["language"]} ({item["frac"]:.1f}%)</text>'
        contents += f"</g>\n"
    if x < INNER_WIDTH:
        width = INNER_WIDTH - x
        contents += f'    <rect mask="url(#lang-mask)" x="{x:.0f}" y="0" width="{(width+1):.0f}" height="8" fill="#888" />\n'

    contents += "  </g>\n"
    contents += "</svg>\n"

    os.makedirs("images", exist_ok=True)
    with open("images/lang.svg", "w") as f:
        f.write(contents)


def add_to_history(languages):
    FILENAME = "src/lang_history.csv"
    INDEX_COL_NAME = "Date"

    line = {l["language"]: round(l["frac"], 1) for l in languages}
    date = dt.date.today().strftime("%d/%m/%Y")
    line = pd.DataFrame(
        line,
        index=[
            date,
        ],
    )

    try:
        history = pd.read_csv(FILENAME, index_col=INDEX_COL_NAME)
        history = pd.concat([history, line], axis=0, ignore_index=False)
        history.fillna(0, inplace=True)
    except FileNotFoundError:
        history = line
    history.sort_values(by=date, axis=1, inplace=True, ascending=False)

    if len(history.index) > 1:
        values1 = history.iloc[-2:-1, 0:NUM_LANGUAGES].reset_index(drop=True)
        values2 = history.iloc[-1:, 0:NUM_LANGUAGES].reset_index(drop=True)
        if values1.equals(values2):
            history.drop(history.tail(1).index, inplace=True)

    history.to_csv(FILENAME, index_label=INDEX_COL_NAME)
    return history


def get_colours(languages):
    FILENAME = "src/colours.csv"
    INDEX_COL_NAME = "Language"

    colours = {l["language"]: l["color"] for l in languages}

    try:
        old_colours = pd.read_csv(FILENAME, index_col=INDEX_COL_NAME)
        for index, row in old_colours.iterrows():
            colours[index] = row["Color"]
    except FileNotFoundError:
        pass

    pd.DataFrame.from_dict(colours, orient="index", columns=["Color"]).to_csv(
        FILENAME, index_label=INDEX_COL_NAME
    )
    return colours


def render_history(history, colours):
    INNER_HEIGHT = HEIGHT - 60
    contents = (
        f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none" role="img" xmlns="http://www.w3.org/2000/svg">\n'
        f"  <style>\n{STYLE}  </style>\n"
        f'  <rect x="0.5" y="0.5" rx="4.5" width="{WIDTH-1}" height="{HEIGHT-1}" stroke="#888" stroke-opacity="1" fill="none" />\n'
        f'  <g transform="translate(15,25)"><text x="0" y="0" class="header">Language History</text></g>\n'
        f'  <g transform="translate(15,45)">\n'
        f'    <rect x="0" y="0" width="{INNER_WIDTH}" height="{INNER_HEIGHT}" fill="#888" />\n'
    )

    start_date = dt.datetime.strptime(history.index[0], "%d/%m/%Y").date()
    end_date = dt.datetime.strptime(history.index[-1], "%d/%m/%Y").date()
    duration = (end_date - start_date).days
    x_scale = float(INNER_WIDTH) / float(duration)
    y_scale = float(INNER_HEIGHT) / 100.0

    history = history.iloc[:, 0:NUM_LANGUAGES]
    sum = history.sum(axis=1)
    for col in reversed(history.columns):
        color = colours[col]
        list = ""
        for index, value in zip(sum.index, sum.values):
            i = dt.datetime.strptime(index, "%d/%m/%Y").date()
            x = int(float((i - start_date).days) * x_scale)
            y = int(INNER_HEIGHT - float(value) * y_scale)
            list += f"{x},{y} "
        list += f"{INNER_WIDTH},{INNER_HEIGHT} 0,{INNER_HEIGHT}"
        contents += f'    <polygon points="{list}" fill="{color}" />\n'
        sum -= history[col]

    contents += "  </g>\n"
    contents += "</svg>\n"

    os.makedirs("images", exist_ok=True)
    with open("images/history.svg", "w") as f:
        f.write(contents)


def main():
    excluded = [
        "*:CMake",
        "*:Kotlin",
        "dotfiles:*",
        "tftools:*",
        "sportratings:C++",
        "sportratings:C",
    ]

    response = post(QUERY)
    if "errors" in response:
        print(response.errors)
    repositories = response["data"]["viewer"]["repositories"]["nodes"]

    languages = extract_languages(repositories, excluded)
    history = add_to_history(languages)
    colours = get_colours(languages)

    render_most_used(languages)
    render_history(history, colours)


if __name__ == "__main__":
    main()
