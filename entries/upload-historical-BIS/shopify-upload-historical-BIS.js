const csv = require('csv-parser');
const fs = require('fs');
const shell = require('shelljs');

const publicToken = 'REPLACE_WITH_YOUR_PUBLIC_TOKEN'

fs.createReadStream('REPLACE_WITH_PATH_TO_CSV')  
  .pipe(csv())
  .on('data', (row) => {
    let email = row.customer_email
    let variant = row.variant_id
    let str = 'PUBLICTOKEN=' + publicToken + 'EMAIL=' + email + ' VARIANT=' + variant + ' ./bis.sh'
    shell.exec(str);

  })
  .on('end', () => {
    console.log('CSV file successfully processed');
  });