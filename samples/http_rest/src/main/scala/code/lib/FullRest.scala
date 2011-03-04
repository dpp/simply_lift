package code
package lib

import model._

import net.liftweb._
import common._
import http._
import rest._
import util._
import Helpers._
import json._
import scala.xml._

/**
 * A full REST example
 */
object FullRest extends RestHelper {

  // Serve /api/item and friends
  serve( "api" / "item" prefix {
    
    // /api/item returns all the items
    case Nil JsonGet _ => Item.inventoryItems: JValue

    // /api/item/count gets the item count
    case "count" :: Nil JsonGet _ => JInt(Item.inventoryItems.length)

    // /api/item/item_id gets the specified item (or a 404)
    case Item(item) :: Nil JsonGet _ => item: JValue

    // /api/item/search/foo or /api/item/search?q=foo
    case "search" :: q JsonGet _ =>
      (for {
        searchString <- q ::: S.params("q")
        item <- Item.search(searchString)
      } yield item).distinct: JValue

    // DELETE the item in question
    case Item(item) :: Nil JsonDelete _ => 
      Item.delete(item.id).map(a => a: JValue)

    // PUT adds the item if the JSON is parsable
    case Nil JsonPut Item(item) -> _ => Item.add(item): JValue
    
    // POST if we find the item, merge the fields from the 
    // the POST body and update the item
    case Item(item) :: Nil JsonPost json -> _ => 
      Item(mergeJson(item, json)).map(Item.add(_): JValue)

    // Wait for a change to the Items
    // But do it asynchronously
    case "change" :: Nil JsonGet _ =>
      RestContinuation.async {
        f => {
          // schedule a "Null" return if there's no other answer
          // after 110 seconds
          Schedule.schedule(() => f(JNull), 110 seconds)

          // register for an "onChange" event.  When it
          // fires, return the changed item as a response
          Item.onChange(item => f(item: JValue))
        }
      }
  })
}
