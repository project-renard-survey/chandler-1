/////////////////////////////////////////////////////////////////////////////
// Name:        _effects.i
// Purpose:     wxEffects
//
// Author:      Robin Dunn
//
// Created:     18-June-1999
// RCS-ID:      $Id: _effects.i 5166 2005-04-29 01:36:53Z davids $
// Copyright:   (c) 2003 by Total Control Software
// Licence:     wxWindows license
/////////////////////////////////////////////////////////////////////////////

// Not a %module


//---------------------------------------------------------------------------
%newgroup

%{
#include <wx/effects.h>
%}

//---------------------------------------------------------------------------

class wxEffects: public wxObject
{
public:
    // Assume system colours
    wxEffects();

    wxColour GetHighlightColour() const;
    wxColour GetLightShadow() const;
    wxColour GetFaceColour() const;
    wxColour GetMediumShadow() const;
    wxColour GetDarkShadow() const;

    void SetHighlightColour(const wxColour& c);
    void SetLightShadow(const wxColour& c);
    void SetFaceColour(const wxColour& c);
    void SetMediumShadow(const wxColour& c);
    void SetDarkShadow(const wxColour& c);

    void Set(const wxColour& highlightColour, const wxColour& lightShadow,
             const wxColour& faceColour, const wxColour& mediumShadow,
             const wxColour& darkShadow);

    // Draw a sunken edge
    void DrawSunkenEdge(wxDC& dc, const wxRect& rect, int borderSize = 1);

    // Tile a bitmap
    bool TileBitmap(const wxRect& rect, wxDC& dc, wxBitmap& bitmap);

};


//---------------------------------------------------------------------------
