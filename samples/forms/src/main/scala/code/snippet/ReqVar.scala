package code
package snippet

import net.liftweb._
import http._
import common._
import util.Helpers._
import scala.xml.NodeSeq

object ReqVar {
  private object name extends RequestVar("")
  private object age extends RequestVar("0")
  private object whence extends RequestVar(S.referer openOr "/")

  def render = {
    val w = whence.is

    def process() {
      asInt(age.is) match {
        case Full(a) if a < 13 => S.error("Too young!")
        case Full(a) => {
          S.notice("Name: "+name)
          S.notice("Age: "+a)
          S.redirectTo(whence)
        }
        
        case _ => S.error("Age doesn't parse as a number")
      }
    }

    "name=name" #> SHtml.textElem(name, "id" -> "the_name") &
    "name=age" #> (SHtml.textElem(age) ++ 
                   SHtml.hidden(() => whence.set(w))) &
    "type=submit" #> SHtml.onSubmitUnit(process)
  }
}
