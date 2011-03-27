package code
package lib

import comet._

import net.liftweb._
import common._
import http._
import rest.RestHelper
import util._
import Helpers._

// it's a RestHelper
object ShareCart extends RestHelper {
  // private state
  private var carts: Map[String, (Long, Cart)] = Map()

  // given a Cart, generate a unique sharing code
  def codeForCart(cart: Cart): String = synchronized {
    val ret = Helpers.randomString(12)

    carts += ret -> (10.minutes.later.millis -> cart)

    ret
  }

  /**
   * Generate the right link to this cart
   */
  def generateLink(cart: Cart): String = {
    S.hostAndPath + "/co_shop/"+codeForCart(cart)
  }

  // An extractor that converts a String to a Cart, if
  // possible
  def unapply(code: String): Option[Cart] = synchronized {
    carts.get(code).map(_._2)
  }

  // remove any carts that are 10+ minutes old
  private def cleanup() {
    val now = Helpers.millis
    synchronized{
      carts = carts.filter{
        case (_, (time, _)) => time > now
      }
    }
    Schedule.schedule(() => cleanup(), 5 seconds)
  }
  
  // clean up every 5 seconds
  cleanup()

  // the REST part of the code
  serve {
    // match the incoming URL
    case "co_shop" :: ShareCart(cart) :: Nil Get _ => {
      // set the cart
      TheCart.set(cart)
      
      // send the SetNewCart message to the CometCart
      S.session.foreach(
        _.sendCometActorMessage("CometCart", Empty,
                                SetNewCart(cart)))

      // redirect the browser to /
      RedirectResponse("/")
    }
  }
}
