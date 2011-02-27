package code
package lib

import comet._

import net.liftweb._
import common._
import http._
import rest.RestHelper
import util._
import Helpers._

object ShareCart extends RestHelper {
  private var carts: Map[String, (Long, Cart)] = Map()

  def codeForCart(cart: Cart): String = synchronized {
    val ret = Helpers.randomString(12)

    carts += ret -> ((millis + 10 minutes).millis -> cart)

    ret
  }

  /**
   * Generate the right link to this cart
   */
  def generateLink(cart: Cart): String = {
    S.hostAndPath + "/co_shop/"+codeForCart(cart)
  }

  def unapply(code: String): Option[Cart] = synchronized {
    carts.get(code).map{
      case (_, cart) =>
        // carts -= code
        cart
    }
  }

  private def cleanup() {
    val now = Helpers.millis
    synchronized{
      carts = carts.filter{
        case (_, (time, _)) => time > now
      }
    }
    Schedule.schedule(() => cleanup(), 5 seconds)
  }

  cleanup()

  serve {
    case "co_shop" :: ShareCart(cart) :: Nil Get _ =>
      for {
        sess <- S.session
      } {
        TheCart.set(cart)
        sess.sendCometActorMessage("CometCart", Empty, SetNewCart(cart))
      }

      RedirectResponse("/")
  }
}
