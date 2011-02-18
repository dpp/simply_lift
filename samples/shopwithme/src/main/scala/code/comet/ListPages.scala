package code
package comet

import lib._

import net.liftweb._
import common._
import http._
import util._
import js._
import js.jquery._
import JsCmds._
import scala.xml.NodeSeq
import Helpers._

/**
 * The list of pages being viewed in this session
 */
class ListPages extends CometActor {
  /**
   * Draw yourself
   */
  def render = {
    "#listPagesContents" #> (
      "tbody" #> 
      Helpers.findOrCreateId(id =>  // make sure tbody has an id
        // when the cart contents updates
        WiringUI.history(SessionPresenceInfo.pages) {
          (old, nw, ns) => {
            // capture the tr part of the template
            val theTR = ("tr ^^" #> "**")(ns)
            
            // build a row out of the page view info
            def html(ci: (String, ParsePath)): NodeSeq = 
              ("tr [id]" #> ci._1 & "td *" #> ci._2.toString)(theTR)
            
            // calculate the delta between the lists and
            // based on the deltas, emit the current jQuery
            // stuff to update the display
            JqWiringSupport.calculateDeltas(old, nw, id)(_._1, html _)
          }
        }))
  }
}
