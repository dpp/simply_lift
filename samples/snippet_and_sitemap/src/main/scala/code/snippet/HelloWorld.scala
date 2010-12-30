package code
package snippet

import lib._

import net.liftweb._
import util.Helpers._
import common._
import java.util.Date

class HelloWorld {
  lazy val date: Box[Date] = DependencyFactory.inject[Date] // inject the date

  // replace the contents of the element with id "time" with the date
  def render = "* *" #> date.map(_.toString)
}

