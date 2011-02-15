package code
package comet

import lib._

import net.liftweb._
import http._
import util._
import js._
import JsCmds._
import scala.xml.NodeSeq
import Helpers._

object TheCart extends SessionVar(new Cart())

class CometCart extends CometActor {
  private var cart = TheCart.get

  def render = Noop

  override def fixedRender = 
    ("#contents" #> (
      "tbody" #> 
      Helpers.findOrCreateId(id => 
        WiringUI.history(cart.contents) {
          (old, nw, ns) => {
            val ol = old.map(_.toList) openOr Nil
            val nwl = nw.toList

            def html(ci: CartItem): NodeSeq = 
              ("tr ^^" #> "**" andThen "tr [id]" #> ci.id & "td *" #> ci.name)(ns)

            Helpers.delta(ol, nwl) {
              case RemoveDelta(ci) => new JsCmd {
                def toJsCmd = "jQuery('#'+"+ci.id.encJs+").remove();"
                }

              case AppendDelta(ci) => 
                new JsCmd {
                  val toJsCmd = 
                    fixHtmlFunc("inline", html(ci)) {
                      "jQuery('#'+"+id.encJs+").append("+
                      _+
                      ");"}
                }

              case InsertAtStartDelta(ci) => 
                new JsCmd {
                  val toJsCmd = 
                    fixHtmlFunc("inline", html(ci)) {
                      "jQuery('#'+"+id.encJs+").prepend("+
                      _+
                      ");"}
                }

              case InsertAfterDelta(ci, prior) => 
                new JsCmd {
                  val toJsCmd = 
                    fixHtmlFunc("inline", html(ci)) {
                      "jQuery('#'+"+prior.id.encJs+").after("+
                      _+
                      ");"}
                }
            }
          }
        })) &
     "#total" #> WiringUI.asText(cart.subtotal))(defaultHtml)
     
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
