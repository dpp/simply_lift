package code
package snippet

import net.liftweb._
import http._
import common._
import util.Helpers._
import scala.xml.NodeSeq

/**
 * A stateful snippet. The state associated with this
 * snippet is in instance variables 
 */
class Stateful extends StatefulSnippet {
  // state unique to this instance of the stateful snippet
  private var name = ""
  private var age = "0"

  // capture from whence the user came so we
  // can send them back
  private val whence = S.referer openOr "/"

  // StatefulSnippet requires an explicit dispatch
  // to the method.
  def dispatch = {case "render" => render}

  // associate behavior with each HTML element
  def render = 
    "name=name" #> SHtml.text(name, name = _, "id" -> "the_name") &
    "name=age" #> SHtml.text(age, age = _) &
    "type=submit" #> SHtml.onSubmitUnit(process)

  // process the form
  private def process() =
    asInt(age) match {
      case Full(a) if a < 13 => S.error("Too young!")
      case Full(a) => {
        S.notice("Name: "+name)
        S.notice("Age: "+a)
        S.redirectTo(whence)
      }
      
      case _ => S.error("Age doesn't parse as a number")
    }
}
