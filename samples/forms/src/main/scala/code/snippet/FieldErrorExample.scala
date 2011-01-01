package code
package snippet

import net.liftweb._
import http._
import common._
import util.Helpers._
import scala.xml.NodeSeq

class FieldErrorExample extends StatefulSnippet {
  private var name = ""
  private var age = "0"
  private val whence = S.referer openOr "/"

  def dispatch = {case _ => render}

  def render = {
    def process() {
      asInt(age) match {
        case Full(a) if a < 13 => S.error("age", "Too young!")
        case Full(a) => {
          S.notice("Name: "+name)
          S.notice("Age: "+a)
          S.redirectTo(whence)
        }
        
        case _ => S.error("Age doesn't parse as a number")
      }
    }

    "name=name" #> SHtml.text(name, name = _, "id" -> "the_name") &
    "name=age" #> SHtml.text(age, age = _) &
    "type=submit" #> SHtml.onSubmitUnit(process)
  }
}
