__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2003 Open Source Applications Foundation"
__license__ = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

from repository.item.Item import Item
import wx


class Style(Item):

    def __init__(self, *arguments, **keywords):
        super (Style, self).__init__ ( *arguments, **keywords)


class CharacterStyle(Style):

    def __init__(self, *arguments, **keywords):
        super (CharacterStyle, self).__init__ ( *arguments, **keywords)

        
class Font(wx.Font):
    def __init__(self, characterStyle):
        family = wx.DEFAULT
        size = 12
        style = wx.NORMAL
        underline = False
        weight = wx.NORMAL
        if characterStyle:
            if characterStyle.fontFamily == "SerifFont":
                family = wx.ROMAN
            elif characterStyle.fontFamily == "SanSerifFont":
                family = wx.SWISS
            elif characterStyle.fontFamily == "FixedPitchFont":
                family = wx.MODERN
    
            assert (size > 0)
            size = int (characterStyle.fontSize + 0.5) #round to integer

            for theStyle in characterStyle.fontStyle.split():
                lowerStyle = theStyle.lower()
                if lowerStyle == "bold":
                    weight = wx.BOLD
                elif lowerStyle == "light":
                    weight = wx.LIGHT
                elif lowerStyle == "italic":
                    style = wx.ITALIC
                elif lowerStyle == "underline":
                    underline = True
                
        wx.Font.__init__ (self,
                         size,
                         family,
                         style,
                         weight,
                         underline,
                         characterStyle.fontName)
