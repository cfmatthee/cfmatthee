import axios from "axios";

/**
 * 
 * @param {AxiosRequestConfigData} data 
 * @param {AxiosRequestConfigHeaders} headers 
 * @returns (Promise<any>)
 */
const request = (data) => {
  const token = process.env.GITHUB_TOKEN
  return axios({
    url: 'https://api.github.com/graphql',
    method: 'post',
    headers: {
      Authorization: `token ${token}`,
    },
    data,
  })
}

export { request }
