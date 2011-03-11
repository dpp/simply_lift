package code
package snippet

import model.Item
import comet._

import net.liftweb._
import http._
import sitemap._
import util._
import Helpers._

object AllItemsPage {
  // define the menu item for the page that
  // will display all items
  lazy val menu = Menu.i("Items") / "item" >>
  Loc.Snippet("Items", render)
  
  // display the items
  def render =
    "tbody *" #> renderItems(Item.inventoryItems)

  // for a list of items, display those items
  def renderItems(in: Seq[Item]) =
    "tr" #> in.map(item => {
      "a *" #> item.name &
      "a [href]" #> AnItemPage.menu.calcHref(item) &
      "@description *" #> item.description &
      "@price *" #> item.price.toString &
      "@add_to_cart [onclick]" #>
      SHtml.ajaxInvoke(() => TheCart.addItem(item))})
}

