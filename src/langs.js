import { request } from './utils.js'
import fs from "node:fs";

const fetchTopLangs = async () => {
  const fetcher = () => {
    return request(
      {
        query: `
          query userInfo {
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
      `}
    )
  }

  const res = await fetcher()
  return res
}

const extractLanguages = (repos) => {
  let languages = {}
  for (const node of repos) {
    for (const lang of node.languages.edges) {
      const name = lang.node.name
      const color = lang.node.color
      const size = lang.size
      if (languages[name]) {
        languages[name].size += size
      } else {
        languages[name] = { size, color }
      }
    }
  }
  return languages
}

const analyseLanguages = (languages) => {
  const total = Object.keys(languages)
    .map((key) => ({...languages[key], name: key}))
    .reduce((accum, cur) => accum + cur.size, 0)

  return Object.keys(languages)
    .map((key) => ({name: key, ...languages[key], frac: languages[key].size * 100 / total}))
    .sort((a, b) => b.size - a.size)
}

const renderLanguages = (languages) => {
  const WIDTH = 300
  const HEIGHT = 160
  const INNER_WIDTH = WIDTH - 30

  let style = ''
  style += ".header {font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: #2f80ed; }\n"
  style += ".lang-name {font: 400 11px 'Segoe UI', Ubuntu, Sans-Serif; fill: #888; }\n"

  let content = ''
  content += `<svg width="${WIDTH}" height="${HEIGHT}" viewBox="0 0 ${WIDTH} ${HEIGHT}" fill="none" role="img" xmlns="http://www.w3.org/2000/svg">\n` 
  content += `<style>${style}</style>\n`
  content += `<rect x="0.5" y="0.5" rx="4.5" width="${WIDTH-1}" height="${HEIGHT-1}" stroke="#888" stroke-opacity="1" fill="none" />\n`
  content += `<g transform="translate(15,25)"><text x="0" y="0" class="header">Most Used Languages</text></g>\n`
  content += `<g transform="translate(15,45)">\n`
  content += `<mask id="items-mask"><rect x="0" y="0" width="${INNER_WIDTH}" height="8" rx="5" fill="#fff" /></mask>\n`

  let x = 0
  for (const [index, item] of languages.slice(0, 8).entries()) {
    const width = INNER_WIDTH * item.frac / 100
    content += `<rect mask="url(#items-mask)" x="${x}" y="0" width="${width}" height="8" fill="${item.color}" />\n`
    x += width

    const y = Math.floor(index / 2) * 20 + 25
    const p = (index % 2) * INNER_WIDTH / 2 + 15
    content += `<g transform="translate(${p},${y})">`
    content += `<circle cx="5" cy="5" r="5" fill="${item.color}" />`
    content += `<text x="15" y="10" class="lang-name">${item.name} (${Number(item.frac).toFixed(1)}%)</text>`
    content += `</g>\n`
  }
  if (x < INNER_WIDTH) {
    const width = INNER_WIDTH - x
    content += `<rect mask="url(#items-mask)" x="${x}" y="0" width="${width}" height="8" fill="#888" />\n`
  }

  content += `</g>\n`
  content += '</svg>\n'

  try {
    fs.writeFileSync('images/lang.svg', content)
  } catch (err) {
    console.error(err)
  }
}

// ===============================================================================================
// main script starts here

const generateLanguagesChart = async () => {
  const excluded = ['dotfiles', 'obsidian-setting']

  const data = await fetchTopLangs().then(res => res.data)
  if (data.errors) {
    console.error(data.errors)
  } else {
    const repos = data.data.viewer.repositories.nodes.filter(node => !excluded.includes(node.name))
    const languages = analyseLanguages(extractLanguages(repos))
    renderLanguages(languages)
  }
}

export {generateLanguagesChart}
