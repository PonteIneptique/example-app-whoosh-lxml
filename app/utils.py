from typing import List
from collections import namedtuple
import lxml.etree as ET


NAMESPACES = {
    "a": "http://www.loc.gov/standards/alto/ns-v4#"
}
Line = namedtuple("Line", ["text", "type", "regionId"])


def get_lines(filepath: str) -> List[Line]:
    xml = ET.parse(filepath)
    regions = {
        region.attrib["ID"]: region.attrib["LABEL"]
        for region in xml.xpath("/a:alto/a:Tags/a:OtherTag", namespaces=NAMESPACES)
    }
    lines = []
    for tb in xml.xpath("//a:TextBlock[.//a:TextLine]", namespaces=NAMESPACES):
        rType = regions.get(tb.attrib["TAGREFS"], "Inconnue")
        rId = tb.attrib["ID"]
        for line in tb.xpath(".//a:TextLine//a:String/@CONTENT", namespaces=NAMESPACES):
            lines.append(Line(str(line), rType, rId))
    return lines
