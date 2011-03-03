package code
package lib

import model._

import net.liftweb._
import common._
import http._
import rest._

/**
 * A simple example of a REST style interface
 * using the basic Lift tools
 */
object BasicWithHelper extends RestHelper {
  serve {
    case "simple3" :: "item" :: itemId :: Nil JsonGet _ =>
      for {
        item <- Item.find(itemId) ?~ "Item Not Found"
      } yield JsonResponse(item)

    case "simple3" :: "item" :: itemId :: Nil XmlGet _ =>
      for {
        item <- Item.find(itemId) ?~ "Item Not Found"
      } yield XmlResponse(item)
  }


  serve {
    case "simple4" :: "item" :: FindItem(item) :: Nil JsonGet _ =>
      JsonResponse(item)
    case "simple4" :: "item" :: FindItem(item) :: Nil XmlGet _ =>
      XmlResponse(item)
  }

  serve ( "simple5" / "item" >> {
    case Nil JsonGet _ => JsonResponse(Item.inventoryItems)
    case Nil XmlGet _ => XmlResponse(Item.inventoryItems)
    case FindItem(item) :: Nil JsonGet _ => JsonResponse(item)
    case FindItem(item) :: Nil XmlGet _ => XmlResponse(item)
  })
}
