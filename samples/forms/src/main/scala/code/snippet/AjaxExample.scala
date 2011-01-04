package code
package snippet

import net.liftweb._
import http._
import common._
import util.Helpers._
import js._
import JsCmds._
import JE._
import scala.xml.NodeSeq


object AjaxExample {
  def render = {
    var name = ""
    var age = "0"
    val whence = S.referer openOr "/"

    def process(): JsCmd= {
      Thread.sleep(400)
      asInt(age) match {
        case Full(a) if a < 13 => S.error("age", "Too young!"); Noop
        case Full(a) => {
          RedirectTo(whence, () => {
            S.notice("Name: "+name)
            S.notice("Age: "+a)
          })
        }
        
        case _ => S.error("age", "Age doesn't parse as a number"); Noop
      }
    }

    "name=name" #> SHtml.text(name, name = _, "id" -> "the_name") &
    "name=age" #> SHtml.text(age, age = _) &
    "type=submit" #> ((ns: NodeSeq) => ns ++ SHtml.hidden(process))
  }
}
