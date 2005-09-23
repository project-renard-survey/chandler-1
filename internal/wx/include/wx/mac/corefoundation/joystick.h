/////////////////////////////////////////////////////////////////////////////
// Name:        joystick.h
// Purpose:     wxJoystick class
// Author:      Ryan Norton
// Modified by:
// Created:     2/13/2005
// RCS-ID:      $Id: joystick.h 5168 2005-04-29 23:18:17Z davids $
// Copyright:   (c) Ryan Norton
// Licence:     wxWindows licence
/////////////////////////////////////////////////////////////////////////////

#ifndef _WX_JOYSTICK_H_
#define _WX_JOYSTICK_H_

#if defined(__GNUG__) && !defined(NO_GCC_PRAGMA)
#pragma interface "joystick.h"
#endif

#include "wx/event.h"

class WXDLLEXPORT wxJoystickThread;

class WXDLLEXPORT wxJoystick: public wxObject
{
    DECLARE_DYNAMIC_CLASS(wxJoystick)
 public:

    wxJoystick(int joystick = wxJOYSTICK1);
    virtual ~wxJoystick();

    // Attributes
    ////////////////////////////////////////////////////////////////////////////

    wxPoint GetPosition() const;
    int GetZPosition() const;
    int GetButtonState() const;
    int GetPOVPosition() const;
    int GetPOVCTSPosition() const;
    int GetRudderPosition() const;
    int GetUPosition() const;
    int GetVPosition() const;
    int GetMovementThreshold() const;
    void SetMovementThreshold(int threshold) ;

    // Capabilities
    ////////////////////////////////////////////////////////////////////////////

    bool IsOk() const; // Checks that the joystick is functioning
    int GetNumberJoysticks() const ;
    int GetManufacturerId() const ;
    int GetProductId() const ;
    wxString GetProductName() const ;
    int GetXMin() const;
    int GetYMin() const;
    int GetZMin() const;
    int GetXMax() const;
    int GetYMax() const;
    int GetZMax() const;
    int GetNumberButtons() const;
    int GetNumberAxes() const;
    int GetMaxButtons() const;
    int GetMaxAxes() const;
    int GetPollingMin() const;
    int GetPollingMax() const;
    int GetRudderMin() const;
    int GetRudderMax() const;
    int GetUMin() const;
    int GetUMax() const;
    int GetVMin() const;
    int GetVMax() const;

    bool HasRudder() const;
    bool HasZ() const;
    bool HasU() const;
    bool HasV() const;
    bool HasPOV() const;
    bool HasPOV4Dir() const;
    bool HasPOVCTS() const;

    // Operations
    ////////////////////////////////////////////////////////////////////////////

    // pollingFreq = 0 means that movement events are sent when above the threshold.
    // If pollingFreq > 0, events are received every this many milliseconds.
    bool SetCapture(wxWindow* win, int pollingFreq = 0);
    bool ReleaseCapture();

protected:
    int                 m_joystick;
    wxJoystickThread*   m_thread;
    class wxHIDJoystick* m_hid;
};

#endif
    // _WX_JOYSTICK_H_
