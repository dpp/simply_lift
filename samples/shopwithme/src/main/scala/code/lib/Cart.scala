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
  val contents = ValueCell[List[Item]](Nil)
  val subtotal = contents.lift(_.foldLeft(BigDecimal(0))(_ + _.price))
  val taxableSubtotal = contents.lift(_.filter(_.taxable).
                                      foldLeft(BigDecimal(0))(_ + _.price))
}
