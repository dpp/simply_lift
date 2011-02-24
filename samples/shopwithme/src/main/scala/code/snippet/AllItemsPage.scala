package code
package snippet

import model.Item

import net.liftweb._
import http._
import sitemap._
import sitemap._
import util._
import Helpers._

object AllItemsPage {
  lazy val menu = Menu.i("Items") / "all_items"

  def render =
    "tbody *" #> Item.items.map(
      item => {
        "@name" #> ("a *" #> item.name & 
                    "a [href]" #> Menu.ParamMenuable.toLoc(AnItemPage.menu).calcHref(item)) &
        "@description *" #> item.description &
        "
        })
}

