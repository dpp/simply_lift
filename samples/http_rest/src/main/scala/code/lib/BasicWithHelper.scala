package code
package lib

import model._

import net.liftweb._
import common._
import http._
import rest._
import json._
import scala.xml._

/**
 * A simple example of a REST style interface
 * using the basic Lift tools
 */
object BasicWithHelper extends RestHelper {
  /*
   * Serve the URL, but have a helpful error message when you
   * return a 404 if the item is not found
   */
  serve {
    case "simple3" :: "item" :: itemId :: Nil JsonGet _ =>
      for {
        // find the item, and if it's not found,
        // return a nice message for the 404
        item <- Item.find(itemId) ?~ "Item Not Found"
      } yield item: JValue

    case "simple3" :: "item" :: itemId :: Nil XmlGet _ =>
      for {
        item <- Item.find(itemId) ?~ "Item Not Found"
      } yield item: Node
  }


  
  serve {
    // Prefix notation
    case JsonGet("simple4" :: "item" :: Item(item) :: Nil, _) =>
      // no need to explicitly create a LiftResponse
      // Just make it JSON and RestHelper does the rest
      item: JValue

    // infix notation
    case "simple4" :: "item" :: Item(item) :: Nil XmlGet _ =>
      item: Node
  }

  // serve a bunch of items given a single prefix
  serve ( "simple5" / "item" prefix {
    // all the inventory
    case Nil JsonGet _ => Item.inventoryItems: JValue
    case Nil XmlGet _ => Item.inventoryItems: Node

    // a particular item
    case Item(item) :: Nil JsonGet _ => item: JValue
    case Item(item) :: Nil XmlGet _ => item: Node
  })

  /**
   * Here's how we convert from an Item
   * to JSON or XML depending on the request's
   * Accepts header
   */
  implicit def itemToResponseByAccepts: JxCvtPF[Item] = {
    case (JsonSelect, c, _) => c: JValue
    case (XmlSelect, c, _) => c: Node
  }

  /**
   * serve the response by returning an item
   * (or a Box[Item]) and let RestHelper determine
   * the conversion to a LiftResponse using
   * the itemToResponseByAccepts partial function
   */
  serveJx[Item] {
    case "simple6" :: "item" :: Item(item) :: Nil Get _ => item
    case "simple6" :: "item" :: "other" :: item :: Nil Get _ => 
      Item.find(item) ?~ "The item you're looking for isn't here"
  }

  /**
   * Same as the serveJx example above, but we've
   * used prefixJx to avoid having to copy the path
   * prefix over and over again
   */
  serveJx[Item] {
    "simple7" / "item" prefixJx {
      case Item(item) :: Nil Get _ => item
      case "other" :: item :: Nil Get _ => 
        Item.find(item) ?~ "The item you're looking for isn't here"
    }
  }
  
}
