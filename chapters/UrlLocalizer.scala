package code
package lib

import net.liftweb._
import http._
import provider._
import common._

import java.util.Locale

object UrlLocalizer {
  // capture the old localization function
  val oldLocalizeFunc = LiftRules.localeCalculator

  /**
   * What are the available locales?
   */
  val locales: Map[String, Locale] = 
    Map(Locale.getAvailableLocales.map(l => l.toString -> l) :_*)

  object currentLocale extends RequestVar(Locale.getDefault)

  /**
   * Extract the locale
   */
  def unapply(in: String): Option[Locale] = 
    if (currentLocale.set_?) None // don't duplicate
  else locales.get(in) // if it's a valid locale, it matches

  /**
   * Calculate the Locale
   */
  def calcLocale(in: Box[HTTPRequest]): Locale = 
    if (currentLocale.set_?) currentLocale.get
  else oldLocalizeFunc(in)

  /**
   * Initialize the locale
   */
  def init() {
    // hook into Lift
    LiftRules.localeCalculator = calcLocale

    // rewrite requests with a locale at the head
    // of the path
    LiftRules.statelessRewrite.append {
      case RewriteRequest(ParsePath(UrlLocalizer(locale) :: rest,
                                    _, _,_), _, _) => {
        currentLocale.set(locale)
        RewriteResponse(rest)
      }
    }
  }
}
