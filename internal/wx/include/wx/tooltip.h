/////////////////////////////////////////////////////////////////////////////
// Name:        tooltip.h
// Purpose:     wxToolTip base header
// Author:      Robert Roebling
// Modified by:
// Created:
// Copyright:   (c) Robert Roebling
// RCS-ID:      $Id: tooltip.h 6038 2005-07-18 21:58:47Z davids $
// Licence:     wxWindows licence
/////////////////////////////////////////////////////////////////////////////

#ifndef _WX_TOOLTIP_H_BASE_
#define _WX_TOOLTIP_H_BASE_

#include "wx/defs.h"

#if wxUSE_TOOLTIPS

#if defined(__WXMSW__)
#include "wx/msw/tooltip.h"
#elif defined(__WXMOTIF__)
// #include "wx/motif/tooltip.h"
#elif defined(__WXGTK__)
#include "wx/gtk/tooltip.h"
#elif defined(__WXMAC__)
#include "wx/mac/tooltip.h"
#elif defined(__WXCOCOA__)
#include "wx/cocoa/tooltip.h"
#elif defined(__WXPM__)
#include "wx/os2/tooltip.h"
#endif

#endif
    // wxUSE_TOOLTIPS

#endif
    // _WX_TOOLTIP_H_BASE_
