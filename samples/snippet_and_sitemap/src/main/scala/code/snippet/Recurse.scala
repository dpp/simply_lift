package code
package snippet

import lib._

import net.liftweb._
import util._
import Helpers._
import http._
import scala.xml.NodeSeq

/**
 * The choices
 */
sealed trait Which
final case class First() extends Which
final case class Second() extends Which
final case class Both() extends Which

/**
 * Choose one or both of the templates
 */
class Recurse(which: Which) {
  // choose the template
  def render = which match {
    case First() => "#first ^^" #> "*" // choose only the first template
    case Second() => "#second ^^" #> "*" // choose only the second template
    case Both() => ClearClearable // it's a passthru
  }
}

/**
 * The first template snippet
 */
object FirstTemplate {
  // it's a passthru, but has the notice side effect
  def render(in: NodeSeq) = {
    S.notice("First Template Snippet executed")
    in
  }
}

/**
 * The second template snippet
 */
object SecondTemplate {
  // it's a passthru, but has the notice side effect
  def render(in: NodeSeq) = {
    S.notice("Second Template Snippet executed")
    in
  }
}
