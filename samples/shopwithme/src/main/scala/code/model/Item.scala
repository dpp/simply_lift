package code
package model

import net.liftweb._
import common._
import json._
/**
 * An item in inventory
 */
case class Item(id: String, name: String, 
                description: String,
                price: BigDecimal, taxable: Boolean,
                weightInGrams: Int)

/**
 * The Item companion object
 */
object Item {
  private implicit val formats = net.liftweb.json.DefaultFormats + BigDecimalSerializer

  lazy val items: List[Item] = parse(data).extract[List[Item]]


  def data = 
"""[
  {"id": "1234", "name": "Cat Food",
  "description": "Yummy, tasty cat food",
  "price": 4.25,
  "taxable": true,
  "weightInGrams": 1000
  },
  {"id": "1235", "name": "Dog Food",
  "description": "Yummy, tasty dog food",
  "price": 7.25,
  "taxable": true,
  "weightInGrams": 5000
  },
  {"id": "1236", "name": "Fish Food",
  "description": "Yummy, tasty fish food",
  "price": 2,
  "taxable": false,
  "weightInGrams": 200
  },
  {"id": "1237", "name": "Sloth Food",
  "description": "Slow, slow sloth food",
  "price": 18.33,
  "taxable": true,
  "weightInGrams": 750
  },
]
"""

  def find(id: String): Box[Item] = items.find(_.id == id)

  /**
   * Find all the items with the string in their name or
   * description
   */
  def search(str: String): List[Item] = {
    val strLC = str.toLowerCase()

    items.filter(i =>
      i.name.toLowerCase.indexOf(strLC) >= 0 ||
                 i.description.toLowerCase.indexOf(strLC) >= 0)
  }
    
}


object BigDecimalSerializer extends Serializer[BigDecimal] {
  private val Class = classOf[BigDecimal]

  def deserialize(implicit format: Formats): PartialFunction[(TypeInfo, JValue), BigDecimal] = {
    case (TypeInfo(Class, _), json) => json match {
      case JInt(iv) => BigDecimal(iv)
      case JDouble(dv) => BigDecimal(dv)
      case value => throw new MappingException("Can't convert " + value + " to " + Class)
    }
  }

  def serialize(implicit format: Formats): PartialFunction[Any, JValue] = {
    case d: BigDecimal => JDouble(d.doubleValue)
  }
}
