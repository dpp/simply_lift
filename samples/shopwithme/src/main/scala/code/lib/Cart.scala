package code
package lib

import model.Item

import net.liftweb._
import util._

/**
 * The shopping cart
 */
class Cart {
  /**
   * The current tax rate
   */
  val taxRate = ValueCell(BigDecimal("0.5"))

  /**
   * The contents of the cart
   */
  val contents = ValueCell[Vector[CartItem]](Vector())

  /**
   * The subtotal
   */
  val subtotal = contents.lift(_.foldLeft(BigDecimal(0))(_ + _.price))

  /**
   * The taxable subtotal
   */
  val taxableSubtotal = contents.lift(_.filter(_.taxable).
                                      foldLeft(BigDecimal(0))(_ + _.price))

  /**
   * The weight of the cart
   */
  val weight = contents.lift(_.foldLeft(0)(_ + _.weightInGrams))


}

/**
 * An item in the cart
 */
case class CartItem(item: Item, qnty: Int, id: String = Helpers.nextFuncName)

/**
 * The CartItem companion object
 */
object CartItem {
  implicit def cartItemToItem(in: CartItem): Item = in.item
}
