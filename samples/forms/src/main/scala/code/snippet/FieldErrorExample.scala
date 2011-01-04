package code
package snippet

import net.liftweb._
import http._
import common._
import util.Helpers._
import scala.xml.NodeSeq

/**
 * A StatefulSnippet like Stateful.scala
 */
class FieldErrorExample extends StatefulSnippet {
  private var name = ""
  private var age = "0"
  private val whence = S.referer openOr "/"

  def dispatch = {case _ => render}

  def render =
    "name=name" #> SHtml.text(name, name = _) &
    "name=age" #> SHtml.text(age, age = _) &
    "type=submit" #> SHtml.onSubmitUnit(process)
  
  // like Stateful
  private def process() =
    asInt(age) match {
      // notice the parameter for error corresponds to
      // the id in the Msg span
      case Full(a) if a < 13 => S.error("age", "Too young!")
      case Full(a) => {
        S.notice("Name: "+name)
        S.notice("Age: "+a)
        S.redirectTo(whence)
      }
      
      // notice the parameter for error corresponds to
      // the id in the Msg span
      case _ => S.error("age", "Age doesn't parse as a number")
    }
}
