package code
package snippet

import net.liftweb._
import http._
import util.Helpers._
import scala.xml.NodeSeq

object OnSubmit {
  def render = {
    var name = ""
    var age = 0

    def process() {
      if (age < 13) S.error("Too young!")
      else {
        S.notice("Name: "+name)
        S.notice("Age: "+age)
        S.redirectTo("/")
      }
    }

    "name=name" #> SHtml.onSubmit(name = _) &
    "name=age" #> SHtml.onSubmit(s => asInt(s).foreach(age = _)) &
    "type=submit" #> SHtml.onSubmitUnit(process)
  }
}
