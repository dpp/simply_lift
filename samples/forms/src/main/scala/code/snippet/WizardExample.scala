package code
package snippet

import net.liftweb._
import http._
import wizard._
import util._

/**
 * Define the multi-page input screen
 */
object WizardExample extends Wizard {

  // define the first screen
  val screen1 = new Screen {
    val name = field("Name", "")
    val age = field("Age", 0, minVal(13, "Too Young"))
  }

  // define the second screen
  val screen2 = new Screen {

    // a radio button
    val rad = radio("Radio", "Red", List("Red", "Green", "Blue"))

    // a select
    val sel = select("Select", "Archer", List("Elwood", "Archer", "Madeline"))

    // want a text area... yeah, we got that
    val ta = textarea("Text Area", "")

    // here are password inputs with minimum lenght
    val pwd1 = password("Password", "", valMinLen(6, "Password too short"))

    // and a custom validator
    val pwd2 = password("Password (re-enter)", "", mustMatch _)

    // return a List[FieldError]... there's an implicit conversion
    // from String to List[FieldError] that inserts the field's ID
    def mustMatch(s: String): List[FieldError] = 
      if (s != pwd1.is) "Passwords do not match" else Nil
      
  }

  def finish() {
    S.notice("Name: "+screen1.name)
    S.notice("Age: "+screen1.age)
  }
}
