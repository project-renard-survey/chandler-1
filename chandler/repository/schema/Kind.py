
__revision__  = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2002 Open Source Applications Foundation"
__license__   = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

from model.item.Item import Item
from model.item.ItemRef import RefDict


class Kind(Item):

    def __init__(self, name, parent, kind, **_kwds):

        super(Kind, self).__init__(name, parent, kind, **_kwds)

        # recursion avoidance
        self._attributes['NotFoundAttributes'] = []

    def newItem(self, name, parent):
        '''Create an item of this kind.

        The class instantiated is taken from the Kind's Class attribute if it
        is set. The Item class is used otherwise.'''
        
        return self.getAttribute('Class')(name, parent, self)
        
    def getAttrDef(self, name):

        attrDef = self.getValue('Attributes', name, _attrDict=self._references)
        if attrDef is None:
            attrDef = self.getValue('InheritedAttributes', name,
                                    _attrDict=self._references)
            if attrDef is None:
                return self.inheritAttrDef(name)

        return attrDef

    def inheritAttrDef(self, name):

        if self.hasValue('NotFoundAttributes', name):
            return None
        
        inheritingKinds = self._getInheritingKinds()
        if inheritingKinds is not None:
            cache = True
            for inheritingKind in inheritingKinds:
                if inheritingKind is not None:
                    attrDef = inheritingKind.getAttrDef(name)
                    if attrDef is not None:
                        self.attach('InheritedAttributes', attrDef)
                        return attrDef
                else:
                    cache = False
                    
            if cache:
                self.addValue('NotFoundAttributes', name)

        return None

    def _getInheritingKinds(self):

        if self.hasAttribute('SuperKinds'):
            return self.SuperKinds

        return self._kind._getInheritingKinds()

    def _saveRefs(self, generator, withSchema):

        for attr in self._references.items():
            if self.getAttributeAspect(attr[0], 'Persist', True):
                attr[1]._saveValue(attr[0], self, generator, withSchema)


class KindKind(Kind):

    def __init__(self, name, parent, kind, **_kwds):

        super(KindKind, self).__init__(name, parent, self, **_kwds)


class ItemKind(Kind):

    def _getInheritingKinds(self):

        return None


class SchemaRoot(Item):

    def __init__(self, name, parent, kind, **_kwds):

        super(SchemaRoot, self).__init__(name, parent, kind, **_kwds)

        afterLoadHooks = _kwds.get('_afterLoadHooks', None)
        if afterLoadHooks is not None:
            afterLoadHooks.append(self.afterLoadHook)

    def afterLoadHook(self):

        def apply(item):

            assert not item._attributes.get('NotFoundAttributes', []), item

            for child in item:
                apply(child)

        apply(self)
