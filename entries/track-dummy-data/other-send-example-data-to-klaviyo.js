const names = require('./fullNames')
const products = require('./simplehumanProducts')
const firstNames = require('./firstNames')
const axios = require('axios')

const fns = names.fullNames
const ps = products.products

const createProperties = (allProducts) => {
  const properties = allProducts[Math.floor(Math.random() * allProducts.length)]
  return properties
}

const randomDate = () => {
  const start = new Date(2012, 9, 1)
  const end = new Date(2019, 2, 25)
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()))
}

fns.forEach( email => {
  for (let i = 0; i < 5; i++) {
    const requestObj = {
      token : "MLGtFa",
      event : "Viewed Product",
      customer_properties : {
        $email : email
      },
      properties : createProperties(ps),
      time: randomDate()
    }

    const stPyld = Buffer.from(JSON.stringify(requestObj)).toString('base64')

    axios({
      url: 'https://a.klaviyo.com/api/track?data=' + stPyld,
      method: 'get'
    })
  }
})
