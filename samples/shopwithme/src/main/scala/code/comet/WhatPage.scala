package code
package comet

import lib._

import net.liftweb._
import common._
import http._
import util._
import Helpers._
import scala.xml.NodeSeq

/**
 * A simple presence CometActor
 */
class WhatPage extends CometActor {
  private var thePath: Box[ParsePath] = Empty
  
  override def lifespan = Full(3 seconds)

  def render = NodeSeq.Empty
  
  /**
   * Is this CometActor going to capture the initial Req
   * object?  If yes, override this method and return true
   * and override captureInitialReq to capture the Req.  Why
   * have to explicitly ask for the Req? In order to send Req
   * instances across threads, the Req objects must be snapshotted
   * which is the process of reading the POST or PUT body from the
   * HTTP request stream.  We don't want to do this unless we
   * have to, so by default the Req is not snapshotted/sent.  But
   * if you want it, you can have it.
   */
  override def sendInitialReq_? : Boolean = true

  /**
   * Comet Actors live outside the HTTP request/response cycle.
   * However, it may be useful to know what Request led to the
   * creation of the CometActor.  You can override this method
   * and capture the initial Req object.  Note that keeping a reference
   * to the Req may lead to memory retention issues if the Req contains
   * large message bodies, etc.  It's optimal to capture the path
   * or capture any request parameters that you care about rather
   * the keeping the whole Req reference.
   */
  override protected def captureInitialReq(initialReq: Box[Req]) {
    thePath = initialReq.map(_.path)

    // add the parse path to the list of pages being viewed
    // by this session
    thePath.foreach(p => SessionPresenceInfo.pages.
                    atomicUpdate(lst => (uniqueId -> p) :: lst))

    println("Initied "+name+" path "+thePath)
  }

  override def localShutdown() {
    // remove the page from the list of pages
    SessionPresenceInfo.pages.atomicUpdate(_.filter(_._1 != uniqueId))
    println("Bye "+name+" "+SessionPresenceInfo.pages.get)
  }

  override def localSetup() {
    println("Setting up in "+this+"  888888888888* ")
  }
}

/**
 * Capture the list of all the pages that
 * are being viewed
 */
class PresenceInfo {
  val pages = ValueCell[List[(String, ParsePath)]](Nil)
}

object SessionPresenceInfo extends SessionVar(new PresenceInfo)
