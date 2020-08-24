var _learnq = _learnq || [];
$(document).ajaxComplete(function (event, request, settings) {
  if (settings.url == "/cart/add.js") {
    console.log("added");
    jQuery.getJSON("/cart.js", function (cart) {
      cart.total_price = cart.total_price / 100;
      cart.$value = cart.total_price;
      cart.total_discount = cart.total_discount / 100;
      cart.original_total_price = cart.original_total_price / 100;
      for (var cart_item in cart.items) {
        cart.items[cart_item].original_price =
          cart.items[cart_item].original_price / 100;
        cart.items[cart_item].discounted_price =
          cart.items[cart_item].discounted_price / 100;
        cart.items[cart_item].line_price =
          cart.items[cart_item].line_price / 100;
        cart.items[cart_item].price = cart.items[cart_item].price / 100;
        cart.items[cart_item].original_line_price =
          cart.items[cart_item].original_line_price / 100;
      }
      if (typeof item !== "undefined") {
        $.extend(cart, item);
      }
      _learnq.push(["track", "Added to Cart", cart]);
      console.log("sent");
    });
  }
});
