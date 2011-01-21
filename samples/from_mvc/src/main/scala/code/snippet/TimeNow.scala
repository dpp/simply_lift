// make sure this is the snippet package so Lift
// can find the snippet
package code
package snippet

// some inputs
import net.liftweb._
import util._
import Helpers._

// our snippet
object TimeNow {
  // create a function (NodeSeq => NodeSeq)
  // that puts the current time into the
  // body of the incoming Elem
  def render = "* *" #> now.toString
}
