/////////////////////////////////////////////////////////////////////////////
// Name:        _wxPalette.i
// Purpose:     SWIG interface defs for wxPalette
//
// Author:      Robin Dunn
//
// Created:     7-July-1997
// RCS-ID:      $Id: _palette.i 5166 2005-04-29 01:36:53Z davids $
// Copyright:   (c) 2003 by Total Control Software
// Licence:     wxWindows license
/////////////////////////////////////////////////////////////////////////////

// Not a %module


//---------------------------------------------------------------------------

// TODO: Create a typemap for the ctor!

//---------------------------------------------------------------------------

MustHaveApp(wxPalette);

class wxPalette : public wxGDIObject {
public:
    wxPalette(int n, const unsigned char *red, const unsigned char *green, const unsigned char *blue);
    ~wxPalette();

    int GetPixel(byte red, byte green, byte blue);
    
    DocDeclA(
        bool, GetRGB(int pixel, byte* OUTPUT, byte* OUTPUT, byte* OUTPUT),
        "GetRGB(self, int pixel) -> (R,G,B)");

    int GetColoursCount() const;
    bool Ok();

    %pythoncode { def __nonzero__(self): return self.Ok() }
};



//---------------------------------------------------------------------------
