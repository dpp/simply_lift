package code
package comet

import lib._

import net.liftweb._
import common._
import http._
import js.JE._
import js.JsCmds._
import util._
import Helpers._
import scala.xml.NodeSeq

/**
 * A simple presence CometActor
 */
class WhatPage extends CometActor {
  private var thePath: Box[ParsePath] = Empty
  private var lastToken = Helpers.nextFuncName
  
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
    this.addPresence()
  }

  private def addPresence() {
    // add the parse path to the list of pages being viewed
    // by this session
    thePath.foreach(p => SessionPresenceInfo.pages.
                    atomicUpdate(_ + (uniqueId -> p)))
    
  }

  private def removePresence() {
    SessionPresenceInfo.pages.atomicUpdate(_.filter(_._1 != uniqueId))
  }

  private def heartBeat() {
    Schedule.schedule(() => this ! HeartBeat(), 5 seconds)
  }

  override def localSetup() {
    heartBeat()
  }

  override def localShutdown() {
    // remove the page from the list of pages
    removePresence()
  }

  /**
   * This method will be called when there's a change in the long poll
   * listeners.  The method does nothing, but allows you to get a granular
   * sense of how many browsers care about this CometActor.  Note that
   * this method should not block for any material time and if there's
   * any processing to do, use Scheduler.schedule or send a message to this
   * CometActor.  Do not change the Actor's state from this method.
   */
  override protected def listenerTransition(): Unit = {
    if (cometListeners.isEmpty) {
      // we've got zero listeners.  If we have this for more
      // than 3 seconds, remove us
      val token = lastToken // snapshot this
      Schedule.schedule(() => this ! CheckToken(token), 3 seconds)
    } else {
      // update the token to indicate that we've
      // had a listener transition and should not
      // remove ourselves
      lastToken = Helpers.nextFuncName
      this.addPresence() // make sure we're in the list
    }
  }

  override def lowPriority = {
    case HeartBeat() => {
      // a Noop JavaScript function
      partialUpdate(JsRaw(uniqueId+" = 1;"))
      heartBeat() 
    }

    case CheckToken(token) => {
      // the token hasn't changed in 3 seconds (no
      // transition to having listeners), so
      // we remove ourselves from the list
      if (token == lastToken) {
        this.removePresence()
      }
    }
  }
}

private case class CheckToken(token: String)

private case class HeartBeat()

/**
 * Capture the list of all the pages that
 * are being viewed
 */
class PresenceInfo {
  val pages = ValueCell[Set[(String, ParsePath)]](Set())
}



object SessionPresenceInfo extends SessionVar(new PresenceInfo)
