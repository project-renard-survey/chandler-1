///////////////////////////////////////////////////////////////////////////////
// Name:        wx/palmos/stdpaths.h
// Purpose:     wxStandardPaths for PalmOS systems
// Author:      Wlodzimierz ABX Skiba
// Modified by:
// Created:     2005-02-25
// RCS-ID:      $Id: stdpaths.h 5179 2005-04-30 01:45:07Z davids $
// Copyright:   (c) 2005 Wlodzimierz Skiba
// Licence:     wxWindows licence
///////////////////////////////////////////////////////////////////////////////

#ifndef _WX_PALMOS_STDPATHS_H_
#define _WX_PALMOS_STDPATHS_H_

// ----------------------------------------------------------------------------
// wxStandardPaths
// ----------------------------------------------------------------------------

class WXDLLIMPEXP_BASE wxStandardPaths : public wxStandardPathsBase
{
public:
    void SetInstallPrefix(const wxString& prefix) { m_prefix = prefix; }
    wxString GetInstallPrefix() const { return m_prefix; }
    virtual wxString GetConfigDir() const { return m_prefix; }
    virtual wxString GetUserConfigDir() const { return m_prefix; }
    virtual wxString GetDataDir() const { return m_prefix; }
    virtual wxString GetLocalDataDir() const { return m_prefix; }
    virtual wxString GetUserDataDir() const { return m_prefix; }
    virtual wxString GetPluginsDir() const { return m_prefix; }

private:
    wxString m_prefix;
};

#endif // _WX_PALMOS_STDPATHS_H_
