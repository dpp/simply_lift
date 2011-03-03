package code
package lib

import model._

import net.liftweb._
import common._
import http._

/**
 * A simple example of a REST style interface
 * using the basic Lift tools
 */
object BasicExample {
  /*
   * Given a suffix and an item, make a LiftResponse
   */
  private def toResponse(suffix: String, item: Item) =
    suffix match {
      case "xml" => XmlResponse(item)
      case _ => JsonResponse(item)
    }

  /**
   * Find /simple/item/1234.json
   * Find /simple/item/1234.xml
   */
  lazy val findItem: LiftRules.DispatchPF = {
    case Req("simple" :: "item" :: itemId :: Nil, //  path
             suffix, // suffix
             GetRequest) => 
               () => 
                 for {
                   item <- Item.find(itemId)
                 } yield toResponse(suffix, item)
  }

  /**
   * Find /simple2/item/1234.json
   */
  lazy val extractFindItem: LiftRules.DispatchPF = {
    // path with extractor
    case Req("simple2" :: "item" :: FindItem(item) :: Nil, 
             suffix, GetRequest) =>
               // a function that returns the response
               () => Full(toResponse(suffix, item))
  }
}
