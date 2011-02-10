package code
package model

case class Item(id: String, name: String, 
                price: BigDecimal, taxable: Boolean,
                weightInGrams: Int)
