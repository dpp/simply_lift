// make sure this is the snippet package so Lift
// can find the snippet
package code
package snippet

// some inputs
import net.liftweb._
import util._
import Helpers._
import http._
import js.JsCmds._

// our snippet
object ClickMe {
  // variables associated with the request
  private object pos extends RequestVar(0)
  private object cnt extends RequestVar(0)

  // create a function (NodeSeq => NodeSeq)
  // set the onClick method of the button
  def render = {
    // capture our position on the page
    val posOnPage = pos.set(pos.is + 1)

    "button [onclick]" #> 
    SHtml.ajaxInvoke(() => {
      cnt.set(cnt.is + 1) // increment the click count
      Alert("Thanks pos: "+posOnPage+
          " click count "+cnt)
    })
  }
}
