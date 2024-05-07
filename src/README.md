# Profile scripts

These script(s) queries the GitHub GraphQL endpoint. It requires a GitHub personal access token with metadata read permission, passed as an environmental variable called `PROFILE_TOKEN`, to be able to query private repositories. It is intended to run as part of a GitHub Action on a schedule or after a push to main.

## language.py

`language.py` creates two images (`lang.svg` and `history.svg`) and two data files (`lang_history.csv` and `colours.csv`). The current images are shown below.

<p align="center">
    <img src="../images/lang.svg" alt="Most used languages">
    <img src="../images/history.svg" alt="Language history">
</p>

`lang.svg` shows the most used languages in the repository (up to eight). `history.svg` shows an area chart with the changes in the history chart.

### Potential issues

None of these scripts have been extensively tested. It is unknown how the script will behave with few (or zero) languages, or with a small number of history entries. It will also (potentially) require a limit on the maximum amount of time.

## ISC License

Copyright 2024 Chris Matthee

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
