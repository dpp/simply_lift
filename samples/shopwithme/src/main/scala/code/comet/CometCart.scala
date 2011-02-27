package code
package comet

import lib._

import net.liftweb._
import common._
import http._
import util._
import js._
import js.jquery._
import JsCmds._
import scala.xml.NodeSeq
import Helpers._

/**
 * What's the current cart for this session
 */
object TheCart extends SessionVar(new Cart())

/**
 * The current instance of the CometCart
 */
object CometCartInstance extends SessionVar[Box[CometCart]](Empty)

/**
 * The CometCart is the CometActor the represents the shopping cart
 */
class CometCart extends CometActor {
  // our current cart
  private var cart = TheCart.get

  /**
   * Draw yourself
   */
  def render = {
    "#contents" #> (
      "tbody" #> 
      Helpers.findOrCreateId(id =>  // make sure tbody has an id
        // when the cart contents updates
        WiringUI.history(cart.contents) {
          (old, nw, ns) => {
            // capture the tr part of the template
            val theTR = ("tr ^^" #> "**")(ns)
            
            def ciToId(ci: CartItem): String = ci.id + "_" + ci.qnty

            // build a row out of a cart item
            def html(ci: CartItem): NodeSeq = {
              ("tr [id]" #> ciToId(ci) & 
               "@name *" #> ci.name &
               "@qnty *" #> SHtml.
               ajaxText(ci.qnty.toString,
                        s => {
                          TheCart.
                          setItemCnt(ci, 
                                     Helpers.toInt(s))
                        }, "style" -> "width: 20px;") &
               "@del [onclick]" #> SHtml.
             ajaxInvoke(() => TheCart.removeItem(ci)))(theTR)
            }
            
            // calculate the delta between the lists and
            // based on the deltas, emit the current jQuery
            // stuff to update the display
            JqWiringSupport.calculateDeltas(old, nw, id)(ciToId _, html _)
          }
        })) &
    "#subtotal" #> WiringUI.asText(cart.subtotal) & // display the subttotal
    "#tax" #> WiringUI.asText(cart.tax) & // display the tax
    "#total" #> WiringUI.asText(cart.total) // display the total
  }
   
  /**
   * Process messages from external sources
   */
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
