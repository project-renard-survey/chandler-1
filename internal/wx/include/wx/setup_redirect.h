/*
 * wx/setup.h
 *
 * This file should not normally be used, except where makefiles
 * have not yet been adjusted to take into account of the new scheme
 * whereby a setup.h is created under the lib directory.
 *
 * Copyright:   (c) Vadim Zeitlin
 * RCS-ID:      $Id: setup_redirect.h 6038 2005-07-18 21:58:47Z davids $
 * Licence:     wxWindows Licence
 */

#ifdef __WXMSW__
#include "wx/msw/setup.h"
#else
#error Please adjust your include path to pick up the wx/setup.h file under lib first.
#endif

