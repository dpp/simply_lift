package code
package snippet

import net.liftweb._
import http._
import scala.xml.NodeSeq

/**
 * A snippet that grabs the query parameters
 * from the form POST and processes them
 */
object DumbForm {
  def render(in: NodeSeq): NodeSeq = {

    // use a Scala for-comprehension to evaluate each parameter
    for {
      r <- S.request if r.post_? // make sure it's a post
      name <- S.param("name") // get the name field
      age <- S.param("age") // get the age field
    } {
      // if everything goes as expected,
      // display a notice and send the user
      // back to the home page
      S.notice("Name: "+name)
      S.notice("Age: "+age)
      S.redirectTo("/")
    }

    // pass through the HTML if we don't get a post and
    // all the parameters
    in
  }
}
