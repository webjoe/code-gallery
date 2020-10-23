var _learnq = _learnq || []

function sendViewedProduct(item){
  _learnq.push(["track", "Viewed Product", item])
}

function sendAddedToCart(item){
  _learnq.push(['track', 'Added to Cart', item]);
}

function getProductVariant(callback){
  product_handle = product_handle = location.href.split( "/" ).pop().split( "?" )[0]
  product_id = location.href.split( "variant=" )[1]
  jQuery.getJSON("/products/"+product_handle+".js", function(product) {
    var variant_info = {}
    for (variantIdx in product["variants"]) {
      if (product["variants"][variantIdx]["id"] == product_id){
        variant_info = product["variants"][variantIdx]
      }
    }
    variant_info["url"] = location.href
    var item = {
      Name: product.title,
      ProductID: product.id,
      Categories: {{ product.collections|map:"title"|json }},
      Tags: product.tags,
      ImageURL: "https:"+product.featured_image,
      URL: location.href.split( "/" )[0] + "//" + location.href.split( "/" )[2]+product.url,
      Brand: product.vendor,
      Price: product.price/100,
      CompareAtPrice: product.compare_at_price_max/100,
      Variant: variant_info
    }
    callback(item);
  })
}

getProductVariant(sendViewedProduct)
$("PRODUCT_OPTION_FORM_SELECTOR :input").change(function() {
  getProductVariant(sendViewedProduct)
})

$("ADDED_TO_CART_BUTTON_SELECTOR").on("click", function() {
  getProductVariant(sendAddedToCart)
})
