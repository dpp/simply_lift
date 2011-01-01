package code
package snippet

import net.liftweb._
import http._

class ScreenExample extends LiftScreen {
  val name = field("Name", "")
  val age = field("Age", 0, minVal(13, "Too Young"))

  def finish() {
    S.notice("Name: "+name)
    S.notice("Age: "+age)
  }
}
