__copyright__ = "Copyright (c) 2005 Open Source Applications Foundation"
__license__ = "http://osafoundation.org/Chandler_0.1_license_terms.htm"
__parcel__ = "osaf.framework.blocks"

import sys
from osaf.framework.blocks import Block
from osaf.framework.blocks import ContainerBlocks
from repository.item.Item import Item
from application import schema
import wx

"""
Classes for dynamically substituting child trees-of-blocks.

The idea is that you've got a block that wants different sets of child blocks
substituted within itself, based on some key (like a content item to be
displayed). The block inherits from this BranchPointBlock class; whenever
synchronizeWidget happens, the appropriate set of child blocks will be swapped
in. This mechanism is managed by a BranchPointDelegate object, which can be
subclassed and/or configured from parcel XML to customize its behavior. 
"""

class BranchSubtree(schema.Annotation):
    """
    A mapping between an Item and the list of top-level blocks ('rootBlocks') 
    that should appear when an Item inheriting from that Kind is displayed. 
    Each rootBlock entry should have its 'position' attribute specified, to 
    enable it to be sorted with other root blocks.)
    """
    schema.kindInfo(annotates=schema.Kind)
    rootBlocks = schema.Sequence(Block.Block, 
                                 inverse=Block.Block.parentBranchSubtrees)

class wxBranchPointBlock(ContainerBlocks.wxBoxContainer):
    """ 
    A widget block that gives its BranchPointBlock a chance to change 
    the tree of blocks within it. 
    """
    def wxSynchronizeWidget(self, useHints=False):
        if self.blockItem.isShown:
            self.blockItem.installTreeOfBlocks()
        super(wxBranchPointBlock, self).wxSynchronizeWidget()
    
class BranchPointBlock(ContainerBlocks.BoxContainer):
    """
    A block that can swap in different sets of child blocks (branch point 
    "subtrees") based on its detailContents. It uses a BranchPointDelegate to 
    do the heavy lifting.
    """    
    colorStyle = schema.One('osaf.framework.blocks.Styles.ColorStyle')

    delegate = schema.One(
        'BranchPointDelegate', inverse = 'blocks', required = True
    )
    detailItem = schema.One(
        schema.Item, defaultValue = None, 
        otherName = 'branchPointDetailItemOwner'
    )
    detailItemCollection = schema.One(
        schema.Item, defaultValue = None
    )
    
    selectedItem = schema.One(
        schema.Item, defaultValue = None, 
        otherName = 'branchPointSelectedItemOwner'
    )

    schema.addClouds(
        copying = schema.Cloud(
            byRef = [delegate,colorStyle,detailItem,selectedItem]
        )
    )

    def instantiateWidget(self):
        return wxBranchPointBlock(self.parentBlock.widget)

    def onSelectItemsEvent (self, event):
        # for the moment, multiple selection means, "select nothing"
        # i.e. multiple selection in the summary view means selecting
        # nothing in the detail view

        # eventually we might want selectedItem to be an iterable
        # of some kind
        items = event.arguments['items']
        if len(items)==1:
            self.selectedItem = items[0]
        else:
            self.selectedItem = None
            
        self.detailItemCollection = \
            self.delegate.getContentsCollection(self.selectedItem,
                                                     event.arguments.get('collection'))
        widget = getattr (self, 'widget', None)
        if widget is not None:
            # eventually results in installTreeOfBlocks()
            widget.wxSynchronizeWidget ()

    def installTreeOfBlocks(self):
        """
        If necessary, replace our children with a tree of blocks appropriate 
        for our content.
        """
        hints = {}
        keyItem = self.delegate._mapItemToCacheKeyItem(
            self.selectedItem, hints)
        newView = self.delegate.getBranchForKeyItem(keyItem)
        if keyItem is None:
            detailItem = None
        else:
            """
              Seems like we should always mark new views with an event boundary
            """
            assert newView is None or newView.eventBoundary
            detailItem = self.delegate._getContentsForBranch(newView, 
                                                             self.selectedItem, 
                                                             keyItem)

        detailItemChanged = self.detailItem is not detailItem
            
        self.detailItem = detailItem
        # For bug 4269 in 0.6: If we've been given a contents collection,
        # it's so that we can put our detailItem in it, to get a notification
        # when that item is deleted. Update the collection if necessary.
        contents = getattr(self, 'contents', None)
        if (contents is not None and contents.first() is not detailItem):
            contents.clear()
            if detailItem is not None:
                contents.add(self.detailItem)

        oldView = self.childrenBlocks.first()
        treeChanged = newView is not oldView

        if treeChanged:
            # get rid of the old view
            if oldView is not None:
                oldView.unRender()

            # attach the new view
            self.childrenBlocks = []
            if newView is not None:
                self.childrenBlocks.append(newView)

        if newView is not None:
            app = wx.GetApp()
            oldIgnoreSynchronizeWidget = app.ignoreSynchronizeWidget
            app.ignoreSynchronizeWidget = False
            try:
                if (detailItemChanged or
                    treeChanged or
                    hints.get ("sendSetContents", False)):
                    newView.postEventByName("SetContents", {
                        'item': detailItem,
                        'collection': self.detailItemCollection})

                if not hasattr (newView, "widget"):
                    newView.render()
                elif detailItemChanged or treeChanged:
                    layoutMethod = getattr(newView, 'Layout', None)
                    if layoutMethod is not None: 
                        layoutMethod()
            finally:
                app.ignoreSynchronizeWidget = oldIgnoreSynchronizeWidget


class BranchPointDelegate(schema.Item):
    """
    A mechanism to map an item to a view: call its getBranchForKeyItem(item)
    to get the view for that item.

    The default implementation is suitable when the item the view to be used;
    it'll be returned as-is (except that a copy will be made if the original's
    in the read-only part of the repository).

    Issues:
     - We'd like to use itemrefs as keys, so reference tracking & cleanup
       would work.
    """

    blocks = schema.Sequence(
        BranchPointBlock,
        inverse = BranchPointBlock.delegate,
        required = True,
    )

    keyUUIDToBranch = schema.Mapping(Block.Block, initialValue = {})

    def deleteCache(self):
        for item in self.keyUUIDToBranch.itervalues():
            if item is not None:
                item.delete (cloudAlias="copying")
        self.keyUUIDToBranch = {}

    def getBranchForKeyItem(self, keyItem):
        """ 
        Given an item, return the view to be used to display it.

        Can be overridden if you don't want the default behavior, which is to 
        cache the views, keyed by a value returned by _mapItemToCacheKeyItem. Misses 
        are handled by _makeBranchForItem.
        """
        branch = None
        if not keyItem is None:
            keyUUID = keyItem.itsUUID
            try:
                branch = self.keyUUIDToBranch[keyUUID]
            except KeyError:
                branch = self._makeBranchForCacheKey(keyItem)
                self.keyUUIDToBranch[keyUUID] = branch
        return branch

    def _mapItemToCacheKeyItem(self, item, hints):
        """ 
        Given an item, determine the item to be used as the cache key.
        Can be overridden; defaults to using the item itself. hints is
        a dictionary that includes domain specific information. See
        the other implementations of _mapItemToCacheKeyItem for more
        information.
        """
        return item

    def _makeBranchForCacheKey(self, keyItem):
        """ 
        Handle a cache miss; build and return a tree-of-blocks for this keyItem. 
        Defaults to using the keyItem itself, copying it if it's in the read-only
        part of the repository. (This behavior fits with the simple case where
        the items are views.)
        """
        return self._copyItem(keyItem, onlyIfReadOnly=True)

    def _copyItem(self, item, onlyIfReadOnly=False):
        """
        Handy utility: Return a copy of this item using its default cloud.
        If onlyIfReadOnly, we'll return the item as-is if it's already in the
        writeable part of the repository.
        """
        # Look up the soup in the repository once per run.
        try:
            userData = self.userData
        except AttributeError:
            userData = self.findPath('//userdata')
            self.userData = userData

        if onlyIfReadOnly and item.itsParent == userData:
            result = item
        else:
            result = item.copy(parent = userData, cloudAlias="copying")
            
        return result

    def _getContentsForBranch(self, branch, item, keyItem):
        """ 
        Given a branch, item and keyItem, 
        return the contents for the branch.
        """
        return item


    def getContentsCollection(self, item, collection):
        """
        Get the actual parent collection used
        """
        return collection
