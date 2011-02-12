package code
package comet

import lib._

import net.liftweb._
import http._
import js._
import JsCmds._

class CometCart extends CometActor {
  val cart = new Cart()

  def render = "#contents" #> WiringUI.toNode(cart.contents) {
    (y: Vector[CartItem], ns) => 
      ("tr *" #> y.map{i => "td *" #> i.name})(ns)
  } & "#total" #> WiringUI.asText(cart.subtotal)

  override def lowPriority = {
    case AddToCart(item) => {
      cart.contents.set(cart.contents.get :+ item)
      partialUpdate(Noop)
    }
  }
}


case class AddToCart(cartItem: CartItem)
