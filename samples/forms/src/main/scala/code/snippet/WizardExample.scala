package code
package snippet

import net.liftweb._
import http._
import wizard._
import util._

class WizardExample extends Wizard {
  val screen1 = new Screen {
    val name = field("Name", "")
    val age = field("Age", 0, minVal(13, "Too Young"))
  }

  val screen2 = new Screen {
    val rad = radio("Radio", "Red", List("Red", "Green", "Blue"))
    val sel = select("Select", "Archer", List("Elwood", "Archer", "Madeline"))
    val ta = textarea("Text Area", "")
    val pwd1 = password("Password", "", valMinLen(6, "Password too short"))
    val pwd2 = password("Password (re-enter)", "", mustMatch _)

    def mustMatch(s: String): List[FieldError] = 
      if (s != pwd1.is) "Passwords do not match" else Nil
      
  }

  def finish() {
    S.notice("Name: "+screen1.name)
    S.notice("Age: "+screen1.age)
  }
}
