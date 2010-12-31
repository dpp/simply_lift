package code
package snippet

import net.liftweb._
import http._
import scala.xml.NodeSeq

object DumbForm {
  def render(in: NodeSeq): NodeSeq = {
    for {
      r <- S.request if r.post_?
      name <- S.param("name")
      age <- S.param("age")
    } {
      S.notice("Name: "+name)
      S.notice("Age: "+age)
      S.redirectTo("/")
    }

    in
  }
}
