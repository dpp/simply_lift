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
   * The contents of the cart
   */
  val contents = ValueCell[Vector[CartItem]](Vector())

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
   * The current tax rate
   */
  val taxRate = ValueCell(BigDecimal("0.07"))

  /**
   * The computed tax
   */
  val tax = taxableSubtotal.lift(_ * taxRate)

  /**
   * The total
   */
  val total = subtotal.lift(_ + tax.get)

  /**
   * The weight of the cart
   */
  val weight = contents.lift(_.foldLeft(zero)(_ +
                                              _.qMult(_.weightInGrams)))

  // Helper methods

  /**
   * A nice constant zero
   */
  def zero = BigDecimal(0)

  /**
   * Add an item to the cart.  If it's already in the cart,
   * then increment the quantity
   */
  def addItem(item: Item) {
    contents.atomicUpdate(v => v.find(_.item == item) match {
      case Some(ci) => v.map(ci => ci.copy(qnty = ci.qnty + 
                                           (if (ci.item == item) 1 else 0)))
      case _ => v :+ CartItem(item, 1)
    })
  }

  /**
   * Set the item quantity.  If zero or negative, remove
   */
  def setItemCnt(item: Item, qnty: Int) {
    if (qnty <= 0) removeItem(item)
    else contents.atomicUpdate(v => v.find(_.item == item) match {
      case Some(ci) => v.map(ci => ci.copy(qnty =
                                           (if (ci.item == item) qnty 
                                            else ci.qnty)))
      case _ => v :+ CartItem(item, qnty)
    })

  }

  /**
   * Removes an item from the cart
   */
  def removeItem(item: Item) {
    contents.atomicUpdate(_.filterNot(_.item == item))
  }
}

/**
 * An item in the cart
 */
case class CartItem(item: Item, qnty: Int, 
                    id: String = Helpers.nextFuncName) {

  /**
   * Multiply the quantity times some calculation on the
   * contained Item (e.g., getting its weight)
   */
  def qMult(f: Item => BigDecimal): BigDecimal = f(item) * qnty
}

/**
 * The CartItem companion object
 */
object CartItem {
  implicit def cartItemToItem(in: CartItem): Item = in.item
}
