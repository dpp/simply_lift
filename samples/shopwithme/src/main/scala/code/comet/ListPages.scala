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
    "tbody *" #> SessionPresenceInfo.pages.map{
      _._2.wholePath.mkString("/", "/", "")
    }.map {
      path => "td *" #> path
    }
  }

  override def localSetup() {
    // make sure we're a dependent on the ValueCell
    // by default, the dependency info will be removed
    // on a reRender
    SessionPresenceInfo.pages.addDependent(this)
  }    

  /**
   * By default, Lift deals with managing wiring dependencies.
   * This means on each full render (a full render will
   * happen on reRender() or on a page load if there have been
   * partial updates.) You may want to manually deal with
   * wiring dependencies.  If you do, override this method
   * and return true
   */
  override protected def manualWiringDependencyManagement = true

  // we'll be poked on the predicate update.  reRender
  // rather than the partial update which is oriented toward
  // the WiringUI world
  override def poke() {
    reRender(false)
  }
}
