"""xfep-xml — UBL 2.1 XML generation for Peruvian electronic invoicing.

Public API::

    from xfep.xml import XmlBuilder, NAMESPACES

    builder = XmlBuilder()
    xml_bytes = builder.build(invoice, company)
"""

from .builder import XmlBuilder
from .namespaces import NAMESPACES

__all__ = ["XmlBuilder", "NAMESPACES"]
