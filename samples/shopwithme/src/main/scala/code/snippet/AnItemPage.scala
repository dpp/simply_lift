package code
package snippet

import model.Item

import net.liftweb._
import http._
import sitemap._

import scala.xml.Text

object AnItemPage {
  // create a parameterized page
  def menu = Menu.param[Item]("Item", Loc.LinkText(i => Text(i.name)),
                              Item.find _, _.id) / "item"
}

