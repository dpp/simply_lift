package code
package comet

import lib._

import net.liftweb._
import http._
import util._
import js._
import js.jquery._
import JsCmds._
import scala.xml.NodeSeq
import Helpers._

object TheCart extends SessionVar(new Cart())

class CometCart extends CometActor {
  private var cart = TheCart.get

  def render = Noop

  override def fixedRender = {
    ("#contents" #> (
      "tbody" #> 
      Helpers.findOrCreateId(id => 
        WiringUI.history(cart.contents) {
          (old, nw, ns) => {
            val theTR = ("tr ^^" #> "**")(ns)

            def html(ci: CartItem): NodeSeq = 
              ("tr [id]" #> ci.id & "td *" #> ci.name)(theTR)
            
            JqWiringSupport.calculateDeltas(old, nw, id)(_.id, html _)
          }
        })) &
     "#total" #> WiringUI.asText(cart.subtotal))
  }

  override def lowPriority = {

    // if someone sends up a new cart
    case SetNewCart(newCart) => {
      // unregister from the old cart
      unregisterFromAllDepenencies()
      theSession.clearPostPageJavaScriptForThisPage()

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
