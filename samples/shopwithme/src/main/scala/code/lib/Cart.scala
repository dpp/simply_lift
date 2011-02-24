package code
package lib

import model.Item

import net.liftweb._
import util._

/**
 * The shopping cart
 */
class Cart {
  def zero = BigDecimal(0)

  def addItem(item: Item) {
    contents.atomicUpdate(v => v.find(_.item == item) match {
      case Some(ci) => v.map(ci => ci.copy(qnty = ci.qnty + 
                                           (if (ci.item == item) 1 else 0)))
      case _ => v :+ CartItem(item, 1)
    })
  }

  /**
   * The current tax rate
   */
  val taxRate = ValueCell(BigDecimal("0.5"))

  /**
   * The contents of the cart
   */
  val contents = ValueCell[Vector[CartItem]](Vector(CartItem(Item.items(2), 1), CartItem(Item.items(1), 2)))

  /**
   * The subtotal
   */
  val subtotal = contents.lift(_.foldLeft(zero)(_ + 
                                                _.qMult(_.price)))

  /**
   * The taxable subtotal
   */
  val taxableSubtotal = contents.lift(_.filter(_.taxable).
                                      foldLeft(zero)(_ + 
                                                     _.qMult(_.price)))

  /**
   * The weight of the cart
   */
  val weight = contents.lift(_.foldLeft(zero)(_ +
                                              _.qMult(_.weightInGrams)))


}

/**
 * An item in the cart
 */
case class CartItem(item: Item, qnty: Int, 
                    id: String = Helpers.nextFuncName) {
  def qMult(f: Item => BigDecimal): BigDecimal = f(item) * qnty
}

/**
 * The CartItem companion object
 */
object CartItem {
  implicit def cartItemToItem(in: CartItem): Item = in.item
}
