package bootstrap.liftweb

import net.liftweb._
import util._
import Helpers._

import common._
import http._
import sitemap._
import Loc._

/**
 * A class that's instantiated early and run.  It allows the application
 * to modify lift's environment
 */
class Boot {
  /**
   * Calculate if the page should be displayed.
   * In this case, it will be visible every other minute
   */
  def displaySometimes_? : Boolean = 
    (millis / 1000L / 60L) % 2 == 0

  def boot {
    // where to search snippet
    LiftRules.addToPackages("code")

    // Build SiteMap
    def sitemap(): SiteMap = SiteMap(
      Menu.i("Home") / "index", // the simple way to declare a menu
      Menu.i("Dumb Form") / "dumb",
      Menu.i("On Submit") / "onsubmit",
      Menu.i("Better Error Handling") / "stateful",
      Menu.i("RequestVars") / "requestvar",
      Menu.i("Field Error") / "fielderror",
      Menu.i("Screen") / "screen",
      Menu.i("Wizard") / "wizard",
      Menu.i("Ajax") / "ajax",
      Menu.i("Query") / "query" >>
      If(() => S.param("q").isDefined, "No Query Param")
    )

    // set the sitemap.  Note if you don't want access control for
    // each page, just comment this line out.
    LiftRules.setSiteMapFunc(() => sitemap())

    //Show the spinny image when an Ajax call starts
    LiftRules.ajaxStart =
      Full(() => LiftRules.jsArtifacts.show("ajax-loader").cmd)
    
    // Make the spinny image go away when it ends
    LiftRules.ajaxEnd =
      Full(() => LiftRules.jsArtifacts.hide("ajax-loader").cmd)

    // Force the request to be UTF-8
    LiftRules.early.append(_.setCharacterEncoding("UTF-8"))

    // Use HTML5 for rendering
    LiftRules.htmlProperties.default.set((r: Req) =>
      new Html5Properties(r.userAgent))    
  }
}
