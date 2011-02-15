package code
package comet

import lib._

import net.liftweb._
import http._
import util._
import js._
import JsCmds._

object TheCart extends SessionVar(new Cart())

class CometCart extends CometActor {
  private var cart = TheCart.get

  def render = Noop

  override def fixedRender = 
    ("#contents" #> (
      "tbody" #> 
      Helpers.findOrCreateId(id => 
        WiringUI.toNode(cart.contents) {
          (y: Vector[CartItem], ns) => 
            ("tr *" #> y.map{i => "td *" #> i.name})(ns)
        })) &
     "#total" #> WiringUI.asText(cart.subtotal))(defaultXml)
     
  override def lowPriority = {

    // if someone sends up a new cart
    case SetNewCart(newCart) => {
      // unregister from the old cart
      unregisterFromAllDepenencies()

      // set the new cart
      cart = newCart

      // do a full reRender including the fixed render piece
      reRender(true)
    }
  }
}

/**
 * Set a new cart for the CometCart
 */
case class SetNewCart(cart: Cart)
