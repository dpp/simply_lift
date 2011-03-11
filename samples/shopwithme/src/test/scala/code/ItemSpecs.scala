package code

import java.io.File

import scala.xml.XML

import org.specs.Specification
import org.specs.runner.JUnit4

import model._

import net.liftweb._
import json._

class ItemTest extends JUnit4(ItemSpecs)

object ItemSpecs extends Specification {

  implicit val formats = net.liftweb.json.DefaultFormats + (new BigDecimalSerializer)

  "Item" should {
    "Serialize" in {
      val i = Item("123", "foo", "foo with extra bar and baz",
                   4, false, 20, 10)

      

      val ret = compact(JsonAST.render(Extraction.decompose(i)))

      ret.length must be > 100
      ret.indexOf("BigD") must_== -1
    }

    "Deserialize" in {
      val i = parse(Item.data).extract[List[Item]].head
      
      i.id must_== "1234"
      i.price must_== BigDecimal("4.25")
    }

    "Round trip" in {

      val i = Item("123", "foo", "foo with extra bar and baz",
                   4, false, 20, 10)

      val ser = compact(render(Extraction.decompose(i)))
      
      i must_== parse(ser).extract[Item]
    }

    "items must be okay" in {
      Item.inventoryItems.head.id must_== "1234"
    }

    "items must be findable" in {
      Item.search("foOD").length must be >= 4
    }

    "items must be findable or not" in {
      Item.search("f#$%%oOD").length must_== 0
    }
  }
}

class BigDecimalSerializer extends Serializer[BigDecimal] {
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
