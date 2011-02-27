package code
package snippet

import model.Item
import comet._

import net.liftweb._
import util._
import Helpers._
import http._
import sitemap._

import scala.xml.Text

object AnItemPage {
  // create a parameterized page
  def menu = Menu.param[Item]("Item", Loc.LinkText(i => Text(i.name)),
                              Item.find _, _.id) / "item" / *
}

class AnItemPage(item: Item) {
  def render = "@name *" #> item.name &
  "@description *" #> item.description &
  "@price *" #> item.price.toString &
  "@add_to_cart [onclick]" #> SHtml.ajaxInvoke(() => TheCart.addItem(item))
}

