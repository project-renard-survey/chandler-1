"""
Basic Unit tests for calendar
"""

__revision__  = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2003 Open Source Applications Foundation"
__license__   = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

import unittest, os

import repository.persistence.XMLRepository as XMLRepository
import repository.parcel.LoadParcels as LoadParcels
import OSAF.contentmodel.calendar.Calendar as Calendar
import OSAF.contentmodel.ContentModel as ContentModel
import OSAF.contentmodel.tests.TestContentModel as TestContentModel
import application.Globals as Globals

import mx.DateTime as DateTime

class CalendarTest(TestContentModel.ContentModelTestCase):

    def testCalendar(self):

        def _verifyCalendarEvent(event):
            self.assertEqual(event.headline, "simple headline")
            self.assertEqual(event.getAttributeValue('headline'),
                              "simple headline")
            self.assertEqual(event.getItemDisplayName(), "simple headline")

            self.assertEqual(event.priority, 3)
            self.assertEqual(event.getAttributeValue('priority'), 3)

            self.assertEqual(event.transparency, "busy")
            self.assertEqual(event.getAttributeValue('transparency'), "busy")

        def _verifyCalendarItems(calendar, location, recurrence, reminder):
            self.assertEqual(calendar.name, "simple calendar")
            self.assertEqual(calendar.getAttributeValue('name'),
                              "simple calendar")

            self.assertEqual(location.name, "simple location")
            self.assertEqual(location.getAttributeValue('name'),
                              "simple location")

        # Check that the globals got created by the parcel
        calendarPath = '//parcels/OSAF/contentmodel/calendar/%s'
        
        self.assertEqual(Calendar.CalendarEventKind,
                         self.rep.find(calendarPath % 'CalendarEvent'))
        self.assertEqual(Calendar.CalendarKind,
                         self.rep.find(calendarPath % 'Calendar'))
        self.assertEqual(Calendar.LocationKind,
                         self.rep.find(calendarPath % 'Location'))
        self.assertEqual(Calendar.RecurrencePatternKind,
                         self.rep.find(calendarPath % 'RecurrencePattern'))
        self.assertEqual(Calendar.ReminderKind,
                         self.rep.find(calendarPath % 'Reminder'))

        # Construct a sample item
        calendarEventItem = Calendar.CalendarEvent("calendarEventItem")
        calendarItem = Calendar.Calendar("calendarItem")
        locationItem = Calendar.Location("locationItem")
        recurrenceItem = Calendar.RecurrencePattern("recurrenceItem")
        reminderItem = Calendar.Reminder("reminderItem")

        # CalendarEvent properties
        calendarEventItem.headline = "simple headline"
        calendarEventItem.priority = 3
        calendarEventItem.transparency = "busy"
        _verifyCalendarEvent(calendarEventItem)

        # Calendar properties
        calendarItem.name = "simple calendar"
        locationItem.name = "simple location"
        _verifyCalendarItems(calendarItem, locationItem,
                             recurrenceItem, reminderItem)

        # Re-examine items
        self._reopenRepository()

        parent = ContentModel.ContentItemParent

        calendarEventItem = parent.find("calendarEventItem")
        calendarItem = parent.find("calendarItem")
        locationItem = parent.find("locationItem")
        recurrenceItem = parent.find("recurrenceItem")
        reminderItem = parent.find("reminderItem")
        
        _verifyCalendarEvent(calendarEventItem)
        _verifyCalendarItems(calendarItem, locationItem,
                             recurrenceItem, reminderItem)

    def testTimeFields(self):
        # Test getDuration
        firstItem = Calendar.CalendarEvent()
        firstItem.startTime = DateTime.DateTime(2003, 2, 1, 10)
        firstItem.endTime = DateTime.DateTime(2003, 2, 1, 11, 30)
        self.assertEqual(firstItem.duration, DateTime.DateTimeDelta(0, 1.5))

        # Test setDuration
        secondItem = Calendar.CalendarEvent()
        secondItem.startTime = DateTime.DateTime(2003, 3, 5, 9)
        secondItem.duration = DateTime.DateTimeDelta(0, 1.5)
        self.assertEqual(secondItem.endTime,
                         DateTime.DateTime(2003, 3, 5, 10, 30))

        # Test changeStartTime
        firstItem.ChangeStart(DateTime.DateTime(2003, 3, 4, 12, 45))
        self.assertEqual(firstItem.duration, DateTime.DateTimeDelta(0, 1.5))
        self.assertEqual(firstItem.startTime,
                         DateTime.DateTime(2003, 3, 4, 12, 45))

    def testDeleteItem(self):
        item = Calendar.CalendarEvent()
        path = item.getItemPath()
        item.delete()
        del item
        itemShouldBeGone = self.rep.find(path)
        self.assertEqual(itemShouldBeGone, None)
        self.rep.commit()

if __name__ == "__main__":
    unittest.main()
