#   Copyright (c) 2003-2007 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from chandlerdb.item.c import CItem, isitem, ItemValue
from chandlerdb.item.ItemError import *
from chandlerdb.util.c import UUID, Nil

from chandlerdb.schema.TypeHandler import TypeHandler
from chandlerdb.schema.Kind import Kind
from chandlerdb.item.PersistentCollections import \
    PersistentCollection, \
    PersistentList, PersistentDict, PersistentSet, PersistentTuple
from chandlerdb.item.Values import Values, References
from chandlerdb.persistence.RepositoryError import NoSuchItemError

from chandlerdb.util.Path import Path
from chandlerdb.util.SAX import ContentHandler


class RefArgs(object):

    def __init__(self, name, item, otherName, ref, **kwds):

        self.name = name
        self.item = item
        self.otherName = otherName
        self.ref = ref
        self.other = None
        self.kwds = kwds

    def _setItem(self, item):

        self.item = item
        other = item.find(self.ref)
        if other is not None:
            self.other = other

        return other

    def _setValue(self, view):

        item = self.item
        other = self.other

        if other is None:
            other = item.find(self.ref)
            if other is None:
                raise DanglingRefError, (item, self.name, self.ref)

        kwds = self.kwds
        item._references._setValue(self.name, other, self.otherName, True,
                                   kwds.get('cardinality'), kwds.get('alias'),
                                   kwds.get('dictKey'), kwds.get('otherKey'),
                                   kwds.get('otherCard'), kwds.get('otherAlias'))

    def _setRef(self):

        if self.other is None:
            other = self.ref
        else:
            other = self.other
            
        kwds = self.kwds
        self.item._references._setRef(self.name, other, self.otherName, True,
                                      kwds.get('cardinality'),
                                      kwds.get('alias'))


class ValueHandler(ContentHandler, TypeHandler):

    def __init__(self, view):

        ContentHandler.__init__(self)
        TypeHandler.__init__(self)
        
        self.view = view

    def startDocument(self):

        self.tagAttrs = []
        self.tags = []
        self.delegates = []
        self.fields = None
        self.tagCounts = []

    def startElement(self, tag, attrs):

        if tag != 'xml' and not self.errorOccurred():
            try:
                self.data = ''
                if attrs is None:
                    attrs = {}

                if self.delegates:
                    delegate = self.delegates[-1]
                    delegateClass = type(delegate)
                else:
                    delegate = self
                    delegateClass = type(self)
        
                method = getattr(delegateClass, tag + 'Start', None)
                if method is not None:
                    method(delegate, self, attrs)

                self.tags.append(tag)
                self.tagAttrs.append(attrs)
            except:
                self.saveException()

    def endElement(self, tag):

        if tag != 'xml' and not self.errorOccurred():
            try:
                withValue = False

                if self.delegates:
                    delegate = self.delegates[-1]
                    if delegate.isValueReady(self):
                        self.delegates.pop()
                        value = delegate.getParsedValue(self, self.data)
                        withValue = True

                if self.delegates:
                    delegate = self.delegates[-1]
                    delegateClass = type(delegate)
                else:
                    delegate = self
                    delegateClass = type(self)
            
                attrs = self.tagAttrs.pop()
                method = getattr(delegateClass, self.tags.pop() + 'End', None)
                if method is not None:
                    if withValue:
                        method(delegate, self, attrs, value=value)
                    else:
                        method(delegate, self, attrs)
            except:
                self.saveException()

    def characters(self, data):

        self.data += data

    def itemStart(self, itemHandler, attrs):

        self.collections = []
        self.withSchema = attrs.get('withSchema', 'False') == 'True'
        self.coreSchema = attrs.get('coreSchema', 'False') == 'True'
        self.kindRef = None
        self.kind = None
        self.attributes = []

    def kindEnd(self, itemHandler, attrs):

        if attrs['type'] == 'uuid':
            self.kindRef = UUID(self.data)
        else:
            self.kindRef = Path(self.data)

        self.kind = self.view._findSchema(self.kindRef, self.withSchema)

    def attributeStart(self, itemHandler, attrs):

        attribute = self.getAttribute(attrs['name'])
        self.attributes.append(attribute)

        cardinality = self.getCardinality(attribute, attrs)
        
        if cardinality == 'list':
            self.collections.append(PersistentList())
        elif cardinality == 'dict':
            self.collections.append(PersistentDict())
        elif cardinality == 'set':
            self.collections.append(PersistentSet())
        else:
            self.valueStart(itemHandler, attrs)

    def valueStart(self, itemHandler, attrs):

        if self._setupTypeDelegate(attrs):
            return

        if (self.tags[-1] == 'attribute' and
            self._setupTypeDelegate(self.tagAttrs[-1])):
            return

        typeName = None

        if attrs.has_key('type'):
            typeName = attrs['type']
        elif (self.tags[-1] == 'attribute' and
              self.tagAttrs[-1].has_key('type')):
            typeName = self.tagAttrs[-1]['type']

        if typeName == 'dict':
            self.collections.append(PersistentDict())
        elif typeName in ('list', 'tuple'):
            self.collections.append(PersistentList())
        elif typeName == 'set':
            self.collections.append(PersistentSet())

    # valueEnd is called when parsing 'dict' or 'list' cardinality values of
    # one type (type specified with cardinality) or of unspecified type
    # (type specified with value) or 'dict' or 'list' type values of 'single'
    # or unspecified cardinality or values of type 'Dictionary' or 'List' of
    # any cardinality. A mess of overloading.
    
    def attributeEnd(self, itemHandler, attrs, **kwds):

        if kwds.has_key('value'):
            value = kwds['value']
        else:
            attribute = self.attributes.pop()
            cardinality = self.getCardinality(attribute, attrs)

            if cardinality in ('list', 'dict', 'set'):
                value = self.collections.pop()
            else:
                typeName = self.getTypeName(attribute, attrs, 'str')
                if typeName in ('list', 'dict', 'set'):
                    value = self.collections.pop()
                elif typeName == 'tuple':
                    value = PersistentTuple(None, None, self.collections.pop())
                else:
                    value = self.makeValue(self.view, typeName, self.data)
                    if attrs.get('eval', 'False') == 'True':
                        typeHandler = self.typeHandler(self.view, value)
                        value = typeHandler.eval(value)
            
        if self.delegates:
            raise ValueError, "while loading '%s.%s' type delegates didn't pop: %s" %(self.name or self.uuid, attrs['name'], self.delegates)

        self.values[attrs['name']] = value

        flags = attrs.get('flags', None)
        if flags is not None:
            flags = int(flags)
            self.values._setFlags(attrs['name'], flags)
            if flags & Values.READONLY:
                if isinstance(value, PersistentCollection):
                    value.setReadOnly()
                elif isinstance(value, ItemValue):
                    value._setReadOnly()

    def valueEnd(self, itemHandler, attrs, **kwds):

        if kwds.has_key('value'):
            value = kwds['value']
        else:
            typeName = self.getTypeName(self.attributes[-1], attrs, None)
            if typeName is None:
                if self.tags[-1] == 'attribute':
                    typeName = self.getTypeName(self.attributes[-1],
                                                self.tagAttrs[-1], 'str')
                else:
                    typeName = 'str'
                
            if typeName in ('list', 'dict', 'set'):
                value = self.collections.pop()
            elif typeName == 'tuple':
                value = PersistentTuple(None, None, self.collections.pop())
            else:
                value = self.makeValue(self.view, typeName, self.data)
                if attrs.get('eval', 'False') == 'True':
                    typeHandler = self.typeHandler(self.view, value)
                    value = typeHandler.eval(value)

        name = attrs.get('name')

        if name is None:
            collection = self.collections[-1]
            if isinstance(collection, set):
                collection._set.add(value)
            else:
                collection._sequence.append(value)
        else:
            name = self.makeValue(self.view, attrs.get('nameType', 'str'), name)
            self.collections[-1]._mapping[name] = value

    def getAttribute(self, name):

        if self.withSchema is False and self.kind is not None:
            return self.kind.getAttribute(name)
        else:
            return None

    def getCardinality(self, attribute, attrs):

        cardinality = attrs.get('cardinality')

        if cardinality is None:
            if attribute is None:
                cardinality = 'single'
            else:
                cardinality = attribute.getAspect('cardinality', 'single')

        return cardinality

    def getTypeName(self, attribute, attrs, default):

        name = None

        if attrs.has_key('typeid'):
            try:
                name = self.view[UUID(attrs['typeid'])].handlerName()
            except KeyError:
                raise TypeError, "Type %s not found" %(attrs['typeid'])

        elif attrs.has_key('typepath'):
            typeItem = self.view.find(Path(attrs['typepath']))
            if typeItem is None:
                raise TypeError, "Type %s not found" %(attrs['typepath'])
            name = typeItem.handlerName()

        elif attrs.has_key('type'):
            name = attrs['type']

        elif attribute is not None:
            attrType = attribute.getAspect('type', None)
            if attrType is not None:
                name = attrType.handlerName()

        return name or default

    def _setupTypeDelegate(self, attrs):

        if attrs.has_key('typeid'):
            try:
                attrType = self.view[UUID(attrs['typeid'])]
            except KeyError:
                raise TypeError, "Type %s not found" %(attrs['typeid'])

            self.delegates.append(attrType)
            attrType.startValue(self)

            return True
        
        elif self.attributes[-1]:
            attrType = self.attributes[-1].getAspect('type')
            if attrType is not None and not attrType.isAlias():
                self.delegates.append(attrType)
                attrType.startValue(self)

                return True

        return False
    
    def xmlValue(cls, view, name, value, tag, attrType, attrCard, attrId,
                 attrs, generator, withSchema):

        if name is not None:
            if not isinstance(name, (str, unicode)):
                attrs['nameType'] = cls.typeHandler(view,
                                                    value).handlerName()
                attrs['name'] = cls.makeString(view, name)
            else:
                attrs['name'] = name

        if attrId is not None:
            attrs['id'] = attrId.str64()

        if attrCard == 'single':
            if attrType is not None and attrType.isAlias():
                aliasType = attrType.type(value)
                if aliasType is None:
                    raise TypeError, "%s does not alias type of value '%s' of type %s" %(attrType.itsPath, value, type(value))
                attrType = aliasType
                attrs['typeid'] = attrType._uuid.str64()

            elif withSchema or attrType is None:
                attrType = cls.typeHandler(view, value)
                attrs['typeid'] = attrType._uuid.str64()

        else:
            attrs['cardinality'] = attrCard

        generator.startElement(tag, attrs)

        if attrCard == 'single':

            if isitem(value):
                raise TypeError, "item %s cannot be stored as a literal value" %(value.itsPath)

            if value is Nil:
                raise ValueError, 'Cannot persist Nil'

            if attrType is not None:
                if not attrType.recognizes(value):
                    raise TypeError, "value '%s' of type %s is not recognized by type %s" %(value, type(value), attrType.itsPath)
                else:
                    attrType.typeXML(value, generator, withSchema)
            else:
                generator.characters(cls.makeString(view, value))
            
        elif attrCard in ('list', 'set'):
            for val in value._itervalues():
                cls.xmlValue(view,
                             None, val, 'value', attrType, 'single',
                             None, {}, generator, withSchema)

        elif attrCard == 'dict':
            for key, val in value._iteritems():
                cls.xmlValue(view,
                             key, val, 'value', attrType, 'single',
                             None, {}, generator, withSchema)
        else:
            raise ValueError, attrCard

        generator.endElement(tag)

    xmlValue = classmethod(xmlValue)


class ItemHandler(ValueHandler):
    """
    A SAX ContentHandler implementation responsible for loading items.
    """
    
    def __init__(self, view, parent, afterLoadHooks, new):

        super(ItemHandler, self).__init__(view)

        self.loading = view.isLoading()
        self.parent = parent
        self.afterLoadHooks = afterLoadHooks
        self.item = None
        self.new = new
        self.values = None
        self.references = None
        
    def refStart(self, itemHandler, attrs):

        if self.tags[-1] == 'item':
            name = attrs['name']
            attribute = self.getAttribute(name)
            self.attributes.append(attribute)

            flags = attrs.get('flags', None)
            if flags is not None:
                flags = int(flags)
                self.references._setFlags(name, flags)
                readOnly = flags & Values.READONLY
            else:
                readOnly = False

            cardinality = self.getCardinality(attribute, attrs)
            if cardinality != 'single':
                if cardinality == 'dict':
                    self.view.logger.warning("Warning, 'dict' cardinality for reference attribute %s on %s is deprecated, use 'list' instead", name, self.name or self.uuid)
                self._setupRefList(name, attribute, readOnly, attrs)

    def _setupRefList(self, name, attribute, readOnly, attrs):

        refList = None
        otherName = self.getOtherName(name, attribute, attrs)

        if attrs.has_key('uuid'):  # some xml parsers don't like 'in' here
            uuid = UUID(attrs['uuid'])
        else:
            uuid = None

        if self.update and attrs.get('operation') == 'append':
            refList = self.item._references.get(name)

        if refList is None:
            refList = self.view._createRefList(None, name, otherName, None,
                                               readOnly, self.new, uuid)
                
        self.collections.append(refList)

    def itemStart(self, itemHandler, attrs):

        super(ItemHandler, self).itemStart(itemHandler, attrs)

        if self.values is None:
            self.values = Values(None)
        if self.references is None:
            self.references = References(None)

        self.refs = []
        self.name = None
        self.cls = None
        self.parentRef = None
        self.isContainer = False
        self.uuid = UUID(attrs.get('uuid'))
        self.version = int(attrs.get('version', '0'))
        self.update = update = attrs.get('update')
        self.delete = delete = attrs.get('delete')

        def _find(spec):

            typeAttr = attrs.get('type', 'path')
            if typeAttr == 'path':
                item = self.parent.find(Path(spec))
            elif typeAttr == 'uuid':
                item = self.parent.find(UUID(spec))
            else:
                raise TypeError, typeAttr

            if item is None:
                raise NoSuchItemError, (spec, self.version)

            return item

        if update is not None:
            item = _find(update)
        elif delete is not None:
            item = _find(delete)
        else:
            item = None

        if item is not None:
            self.item = item
            self.cls = type(item)
            self.version = item._version
            self.name = item.itsName
            self.kind = item.itsKind
            self.uuid = item.itsUUID
            self.parent = item.itsParent

    def itemEnd(self, itemHandler, attrs):

        status = 0

        if self.withSchema:
            status |= CItem.WITHSCHEMA
        if self.coreSchema:
            status |= CItem.CORESCHEMA

        cls = self.cls
        if cls is None:
            if self.kind is None:
                cls = self.view.classLoader.getItemClass()
            else:
                cls = self.kind.getItemClass()

        instance = self.view._instanceRegistry.pop(self.uuid, None)
        if instance is not None:
            if cls is not type(instance):
                raise TypeError, 'Class for item has changed from %s to %s' %(type(instance), cls)
            item = self.item = instance
            status |= item._status & CItem.PINNED
            instance = None

        elif self.update or self.delete:
            item = self.item
            values = item._values
            references = item._references

            for name, value in self.values._dict.iteritems():
                values[name] = value
                item.setDirty(CItem.VDIRTY, name, values, True)
            self.values = values

            for name, value in self.references._dict.iteritems():
                if not isinstance(value, dict):
                    dirty = CItem.VDIRTY
                    item.setAttributeValue(name, value, references,
                                           None, False)
                else:
                    dirty = CItem.RDIRTY
                    references[name] = value
                item.setDirty(dirty, name, references, True)
            self.references = references

            status = item._status | CItem.NDIRTY

        else:
            item = self.item = cls.__new__(cls)

        item._fillItem(self.name, self.parent, self.kind, self.uuid, self.view,
                       self.values, self.references, status, self.version,
                       self.afterLoadHooks, not not self.update)

        if self.isContainer and item._children is None:
            item._children = self.view._createChildren(item, self.new)

        for refArgs in self.refs:
            other = refArgs._setItem(item)
            if self.loading:
                refArgs._setRef()
            elif other is None:
                self.afterLoadHooks.append(refArgs._setValue)
            else:
                refArgs._setValue(self.view)

        self.afterLoadHooks.append(self.setupClass)

        method = attrs.get('afterLoadHook')
        if method is not None:
            self.afterLoadHooks.append(getattr(item, method))
        if hasattr(cls, 'onItemLoad'):
            self.afterLoadHooks.append(item.onItemLoad)
        if self.delete:
            self.afterLoadHooks.append(item.delete)

    def setupClass(self, view):

        if self.update and isinstance(self.item, Kind):
            self.item.flushCaches('attributes')
        elif self.kind is not None:
            self.kind._setupClass(type(self.item))

    def kindEnd(self, itemHandler, attrs):

        assert not self.item

        super(ItemHandler, self).kindEnd(itemHandler, attrs)
        if self.kind is None:
            if self.withSchema:
                self.afterLoadHooks.append(self._setKind)
            else:
                raise ValueError, "While loading %s, kind %s not found" %(self.name or self.uuid, self.kindRef)

    def _setKind(self, view):

        item = self.item
        if item._kind is None:
            self.kind = view.find(self.kindRef)
            if self.kind is None:
                raise ValueError, 'Kind %s not found' %(self.kindRef)
            else:
                item._kind = self.kind
                # give ItemValue instances another chance to cache schema info
                item.itsValues._setItem(item)
                item.itsRefs._setItem(item)

    def parentEnd(self, itemHandler, attrs):

        if attrs['type'] == 'uuid':
            self.parentRef = UUID(self.data)
        else:
            self.parentRef = Path(self.data)

        self.isContainer = attrs.get('container', 'False') == 'True'
        self.parent = self.view.find(self.parentRef)

        if self.parent is None:
            self.afterLoadHooks.append(self._move)

    def _move(self, view):

        if self.item._parent is None:
            self.parent = view.find(self.parentRef)
            if self.parent is None:
                raise ValueError, 'Parent %s not found' %(self.parentRef)
            else:
                self.item.move(self.parent)

    def classEnd(self, itemHandler, attrs):

        self.cls = self.view.classLoader.loadClass(self.data, attrs['module'])

    def nameEnd(self, itemHandler, attrs):

        self.name = self.data

    def refEnd(self, itemHandler, attrs):

        if self.tags[-1] == 'item':
            attribute = self.attributes.pop()
            cardinality = self.getCardinality(attribute, attrs)
            otherCard = attrs.get('otherCard', None)
            
        else:
            cardinality = 'single'
            otherCard = self.tagAttrs[-1].get('otherCard', None)

        if cardinality == 'single':     # cardinality of tag
            typeName = attrs.get('type', 'path')

            if typeName == 'path':
                ref = Path(self.data)
            elif typeName == 'none':
                self.references[attrs['name']] = None
                return
            else:
                ref = UUID(self.data)

            if self.collections:
                refList = self.collections[-1]
                self.refs.append(RefArgs(refList._name, None,
                                         refList._otherName, ref,
                                         otherCard=otherCard,
                                         otherAlias=attrs.get('otherAlias'),
                                         previous=self.refName(attrs, 'previous'),
                                         next=self.refName(attrs, 'next'),
                                         alias=attrs.get('alias')))
            else:
                name = attrs['name']
                otherName = self.getOtherName(name, self.getAttribute(name),
                                              attrs)
                self.refs.append(RefArgs(name, None, otherName, ref,
                                         otherCard=otherCard,
                                         otherAlias=attrs.get('otherAlias')))
        else:
            value = self.collections.pop()
            self.references[attrs['name']] = value
            if value._indexes:
                self.afterLoadHooks.append(value._restoreIndexes)

    def indexEnd(self, itemHandler, attrs):

        if not self.collections:
            raise ValueError, self.tagAttrs[-1]['name']

        refList = self.collections[-1]
        kwds = attrs.copy()
        del kwds['type']
        del kwds['name']
        refList.addIndex(attrs['name'], attrs['type'], **kwds)

    def refName(self, attrs, attr):

        data = attrs.get(attrs, Nil)
        if data is not Nil:
            return self.makeValue(self.view, attrs.get(attr + 'Type', 'str'),
                                  data)
        return None

    def getOtherName(self, name, attribute, attrs):

        otherName = attrs.get('otherName')

        if otherName is None and attribute is not None:
            otherName = self.kind.getOtherName(name, None, None)

        if otherName is None:
            raise TypeError, 'Undefined other endpoint for %s.%s of kind %s' %(self.name or self.uuid, name, self.kind.itsPath)

        return otherName


class ItemsHandler(ContentHandler):

    def __init__(self, view, parent, afterLoadHooks, new):

        super(ItemsHandler, self).__init__()

        self.view = view
        self.parent = parent
        self.afterLoadHooks = afterLoadHooks
        self.new = new

    def startDocument(self):

        self.itemHandler = None
        self.items = []
        
    def startElement(self, tag, attrs):

        if self.exception is None:
            if tag == 'item':
                self.itemHandler = ItemHandler(self.view, self.parent,
                                               self.afterLoadHooks, self.new)
                self.itemHandler.startDocument()

            if self.itemHandler is not None:
                try:
                    self.itemHandler.startElement(tag, attrs)
                    if self.itemHandler.exception is not None:
                        self.exception = self.itemHandler.exception
                        return
                except Exception:
                    self.saveException()
                    return

    def characters(self, data):

        if self.exception is None and self.itemHandler is not None:
            self.itemHandler.characters(data)

    def endElement(self, tag):

        if self.exception is None:
            if self.itemHandler is not None:
                try:
                    self.itemHandler.endElement(tag)
                    if self.itemHandler.exception is not None:
                        self.exception = self.itemHandler.exception
                        return
                except Exception:
                    self.saveException()
                    return
            
            if tag == 'item':
                self.items.append(self.itemHandler.item)
                self.itemHandler.endDocument()
                self.itemHandler = None
