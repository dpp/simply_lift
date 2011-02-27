package code
package snippet

import model._
import comet._
import lib._

import net.liftweb._
import http._
import util.Helpers._
import js._
import JsCmds._
import js.jquery.JqJsCmds._

class Link {
  def request = "* [onclick]" #> SHtml.ajaxInvoke(() => {
    (for {
      template <- TemplateFinder.findAnyTemplate(List("_share_link"))
    } yield ModalDialog(template)) openOr Noop
      
  })

  def close = "* [onclick]" #> SHtml.ajaxInvoke(() => Unblock)

  def generate = {
    val s = ShareCart.generateLink(TheCart)
    "a [href]" #> s & "a *" #> s
  }
}
