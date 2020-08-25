var _learnq = _learnq || []
sendViewedProduct()
$(".product-form :input").change(function() {
  sendViewedProduct()
})

function sendViewedProduct(){
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
    _learnq.push(["track", "Viewed Product test", item])
  })
}
