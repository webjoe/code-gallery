curl \
	--request POST \
	--data 'a='$PUBLICTOKEN'&email='$EMAIL'&variant='$VARIANT'&platform=shopify' \
	https://a.klaviyo.com/api/v1/catalog/subscribe