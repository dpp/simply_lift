package code
package snippet

import model.Item
import comet._

import net.liftweb._
import http._
import sitemap._
import sitemap._
import util._
import Helpers._

object AllItemsPage {
  lazy val menu = Menu.i("Items") / "item" >>
  Loc.Snippet("Items", render)

  def render =
    "tbody *" #> renderItems(Item.items)

  def renderItems(in: Seq[Item]) =
    "tr" #> in.map(item => {
      "a *" #> item.name &
      "@description *" #> item.description &
      "@price *" #> item.price.toString &
      "a [href]" #> AnItemPage.menu.calcHref(item) &
      "@add_to_cart [onclick]" #>
      SHtml.ajaxInvoke(() => TheCart.addItem(item))})
}

