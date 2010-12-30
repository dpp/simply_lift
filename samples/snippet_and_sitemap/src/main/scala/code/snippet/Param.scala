package code
package snippet

import lib._

import net.liftweb._
import util.Helpers._
import common._
import java.util.Date

// capture the page parameter information
case class ParamInfo(theParam: String)

// a snippet that takes the page parameter information
class ShowParam(pi: ParamInfo)  {
  def render = "*" #> pi.theParam
}

