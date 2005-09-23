/////////////////////////////////////////////////////////////////////////////
// Name:        m_style.cpp
// Purpose:     wxHtml module for parsing <style> tag
// Author:      Vaclav Slavik
// RCS-ID:      $Id: m_style.cpp 5166 2005-04-29 01:36:53Z davids $
// Copyright:   (c) 2002 Vaclav Slavik
// Licence:     wxWindows licence
/////////////////////////////////////////////////////////////////////////////

#if defined(__GNUG__) && !defined(NO_GCC_PRAGMA)
#pragma implementation
#endif

#include "wx/wxprec.h"


#include "wx/defs.h"
#if wxUSE_HTML && wxUSE_STREAMS

#ifdef __BORLANDC__
#pragma hdrstop
#endif

#ifndef WXPRECOMP
#endif

#include "wx/html/forcelnk.h"
#include "wx/html/m_templ.h"

FORCE_LINK_ME(m_style)


TAG_HANDLER_BEGIN(STYLE, "STYLE")
    TAG_HANDLER_CONSTR(STYLE) { }

    TAG_HANDLER_PROC(WXUNUSED(tag))
    {
        // VS: Ignore styles for now. We must have this handler present,
        //     because CSS style text would be rendered verbatim otherwise
        return true;
    }

TAG_HANDLER_END(STYLE)


TAGS_MODULE_BEGIN(StyleTag)

    TAGS_MODULE_ADD(STYLE)

TAGS_MODULE_END(StyleTag)

#endif
