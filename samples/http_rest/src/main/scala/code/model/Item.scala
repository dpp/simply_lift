package code
package model

import net.liftweb._
import util._
import Helpers._
import common._
import json._

import scala.xml.Node

/**
 * An item in inventory
 */
case class Item(id: String, name: String, 
                description: String,
                price: BigDecimal, taxable: Boolean,
                weightInGrams: Int, qnty: Int)

/**
 * The Item companion object
 */
object Item {
  private implicit val formats =
    net.liftweb.json.DefaultFormats + BigDecimalSerializer

  private var items: List[Item] = parse(data).extract[List[Item]]

  private var listeners: List[Item => Unit] = Nil

  /**
   * Convert the item to JSON format.  This is
   * implicit and in the companion object, so
   * an Item can be returned easily from a JSON call
   */
  implicit def toJson(item: Item): JValue = Extraction.decompose(item)

  /**
   * Convert a JValue to an Item if possible
   */
  def apply(in: JValue): Box[Item] = Helpers.tryo{in.extract[Item]}

  /**
   * Extract a String (id) to an Item
   */
  def unapply(id: String): Option[Item] = Item.find(id)

  /**
   * Extract a JValue to an Item
   */
  def unapply(in: JValue): Option[Item] = apply(in)

  /**
   * The default unapply method for the case class.
   * We needed to replicate it here because we
   * have overloaded unapply methods
   */
  def unapply(in: Any): Option[(String, String, 
                                String,
                                BigDecimal, Boolean,
                                Int, Int)] = {
    in match {
      case i: Item => Some((i.id, i.name, i.description,
                            i.price, i.taxable,
                            i.weightInGrams, i.qnty))
      case _ => None
    }
  }

  /**
   * Convert an item to XML
   */
  implicit def toXml(item: Item): Node = 
    <item>{Xml.toXml(item)}</item>

  /**
   * Convert a Seq[Item] to JSON format.  This is
   * implicit and in the companion object, so
   * an Item can be returned easily from a JSON call
   */
  implicit def toJson(items: Seq[Item]): JValue = 
    Extraction.decompose(items)

  /**
   * Convert a Seq[Item] to XML format.  This is
   * implicit and in the companion object, so
   * an Item can be returned easily from an XML REST call
   */
  implicit def toXml(items: Seq[Item]): Node = 
    <items>{
      items.map(toXml)
    }</items>

  /**
   * Get all the items in inventory
   */
  def inventoryItems: Seq[Item] = items

  // The raw data
  private def data = 
"""[
  {"id": "1234", "name": "Cat Food",
  "description": "Yummy, tasty cat food",
  "price": 4.25,
  "taxable": true,
  "weightInGrams": 1000,
  "qnty": 4
  },
  {"id": "1235", "name": "Dog Food",
  "description": "Yummy, tasty dog food",
  "price": 7.25,
  "taxable": true,
  "weightInGrams": 5000,
  "qnty": 72
  },
  {"id": "1236", "name": "Fish Food",
  "description": "Yummy, tasty fish food",
  "price": 2,
  "taxable": false,
  "weightInGrams": 200,
  "qnty": 45
  },
  {"id": "1237", "name": "Sloth Food",
  "description": "Slow, slow sloth food",
  "price": 18.33,
  "taxable": true,
  "weightInGrams": 750,
  "qnty": 62
  },
]
"""

  /**
   * Select a random Item
   */
  def randomItem: Item = synchronized {
    items(Helpers.randomInt(items.length))
  }

  /**
   * Find an item by id
   */
  def find(id: String): Box[Item] = synchronized {
    items.find(_.id == id)
  }

  /**
   * Add an item to inventory
   */
  def add(item: Item): Item = {
    synchronized {
      items = item :: items.filterNot(_.id == item.id)
      updateListeners(item)
    }
  }

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

  /**
   * Deletes the item with id and returns the
   * deleted item or Empty if there's no match
   */
  def delete(id: String): Box[Item] = synchronized {
    var ret: Box[Item] = Empty

    val Id = id // an upper case stable ID for pattern matching

    items = items.filter {
      case i@Item(Id, _, _, _, _, _, _) => 
        ret = Full(i) // side effect
        false
      case _ => true
    }

    ret.map(updateListeners)
  }

  /**
   * Update listeners when the data changes
   */
  private def updateListeners(item: Item): Item = {
    synchronized {
      listeners.foreach(f => 
        Schedule.schedule(() => f(item), 0 seconds))

      listeners = Nil
    }
    item
  }

  /**
   * Add an onChange listener
   */
  def onChange(f: Item => Unit) {
    synchronized {
      // prepend the function to the list of listeners
      listeners ::= f
    }
  }
    
}

/**
 * A helper that will JSON serialize BigDecimal
 */
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
