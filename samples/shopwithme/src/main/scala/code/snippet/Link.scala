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

object Link {
  def request = "* [onclick]" #> SHtml.ajaxInvoke(() => {
    (for {
      template <- TemplateFinder.findAnyTemplate(List("_share_link"))
    } yield ModalDialog(template)) openOr Noop
      
  })
}
