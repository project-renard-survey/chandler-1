///////////////////////////////////////////////////////////////////////////////
// Name:        univ/inphand.cpp
// Purpose:     (trivial) wxInputHandler implementation
// Author:      Vadim Zeitlin
// Modified by:
// Created:     18.08.00
// RCS-ID:      $Id: inphand.cpp 5166 2005-04-29 01:36:53Z davids $
// Copyright:   (c) 2000 SciTech Software, Inc. (www.scitechsoft.com)
// Licence:     wxWindows licence
///////////////////////////////////////////////////////////////////////////////

// ===========================================================================
// declarations
// ===========================================================================

// ---------------------------------------------------------------------------
// headers
// ---------------------------------------------------------------------------

#if defined(__GNUG__) && !defined(NO_GCC_PRAGMA)
    #pragma implementation "inphand.h"
#endif

// For compilers that support precompilation, includes "wx.h".
#include "wx/wxprec.h"

#ifdef __BORLANDC__
    #pragma hdrstop
#endif

#ifndef WX_PRECOMP
#endif // WX_PRECOMP

#include "wx/univ/inphand.h"

// ============================================================================
// implementation
// ============================================================================

// ----------------------------------------------------------------------------
// wxInputHandler
// ----------------------------------------------------------------------------

bool wxInputHandler::HandleMouseMove(wxInputConsumer * WXUNUSED(consumer),
                                     const wxMouseEvent& WXUNUSED(event))
{
    return false;
}

bool wxInputHandler::HandleFocus(wxInputConsumer *WXUNUSED(consumer),
                                 const wxFocusEvent& WXUNUSED(event))
{
    return false;
}

bool wxInputHandler::HandleActivation(wxInputConsumer *WXUNUSED(consumer),
                                      bool WXUNUSED(activated))
{
    return false;
}

wxInputHandler::~wxInputHandler()
{
}

