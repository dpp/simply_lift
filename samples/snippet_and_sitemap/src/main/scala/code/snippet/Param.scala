package code
package snippet

import lib._

import net.liftweb._
import util.Helpers._
import common._
import http._
import sitemap._
import java.util.Date

// capture the page parameter information
case class ParamInfo(theParam: String)

// a snippet that takes the page parameter information
class ShowParam(pi: ParamInfo)  {
  def render = "*" #> pi.theParam
}

object Param {
  // Create a menu for /param/somedata
  val menu = Menu.param[ParamInfo]("Param", "Param", 
                                   s => Full(ParamInfo(s)), 
                                   pi => pi.theParam) / "param"
  lazy val loc = menu.toLoc

  def render = "*" #> loc.currentValue.map(_.theParam)
}
