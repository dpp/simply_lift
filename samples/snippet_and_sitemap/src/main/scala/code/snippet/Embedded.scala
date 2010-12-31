package code
package snippet

import lib._

import net.liftweb._
import http._
import util.Helpers._
import common._
import java.util.Date

/**
 * A snippet that lists the name of the current page
 */
object Embedded {
  def from = "*" #> S.location.map(_.name)
}

