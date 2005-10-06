"""
A helper class which sets up and tears down dual RamDB repositories
"""
__revision__  = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2003-2004 Open Source Applications Foundation"
__license__   = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

import unittest, sys, os
import repository.persistence.DBRepository as DBRepository
import repository.item.Item as Item
import application.Parcel as Parcel
import osaf.sharing.Sharing as Sharing
import osaf.sharing.ICalendar as ICalendar
from osaf.pim import ListCollection
import osaf.pim.calendar.Calendar as Calendar
import datetime
import vobject
import cStringIO
from PyICU import ICUtzinfo
from dateutil import tz
from osaf.pim.calendar.Recurrence import RecurrenceRule, RecurrenceRuleSet

class ICalendarTestCase(unittest.TestCase):

    def runTest(self):
        self._setup()
        self.SummaryAndDateTimeImported()
        self.DateImportAsAllDay()
        self.ItemsToVobject()
        self.writeICalendarUnicodeBug3338()
        self.importRecurrence()
        self.importRecurrenceWithTimezone()
        self.exportRecurrence()
        self._teardown()

    def _setup(self):

        rootdir = os.environ['CHANDLERHOME']
        packs = (
         os.path.join(rootdir, 'repository', 'packs', 'chandler.pack'),
        )
        parcelpath = [os.path.join(rootdir, 'parcels')]

        namespaces = [
         'osaf.sharing',
         'osaf.pim.calendar',
        ]

        self.repo = self._initRamDB(packs)
        view = self.repo.view
        self.manager = Parcel.Manager.get(view, path=parcelpath)
        self.manager.loadParcels(namespaces)
        # create a sandbox root
        self.sandbox = Item.Item("sandbox", view, None)
        view.commit()

    def _teardown(self):
        pass

    def _initRamDB(self, packs):
        repo = DBRepository.DBRepository(None)
        repo.create(ramdb=True, stderr=False, refcounted=True)
        view = repo.view
        for pack in packs:
            view.loadPack(pack)
        view.commit()
        return repo

    def Import(self, view, filename):

        path = unicode(os.path.join(os.getenv('CHANDLERHOME') or '.',
                            'parcels', 'osaf', 'sharing', 'tests'))

        sandbox = view.findPath("//sandbox")

        conduit = Sharing.FileSystemConduit(parent=sandbox, sharePath=path,
                                            shareName=filename, view=view)
        format = ICalendar.ICalendarFormat(parent=sandbox)
        self.share = Sharing.Share(parent=sandbox, conduit=conduit,
                                   format=format)
        self.share.get()
        return format

    def SummaryAndDateTimeImported(self):
        format = self.Import(self.repo.view, u'Chandler.ics')
        event = format.findUID('BED962E5-6042-11D9-BE74-000A95BB2738')
        self.assert_(event.displayName == u'3 hour event',
         "SUMMARY of first VEVENT not imported correctly, displayName is %s"
         % event.displayName)
        evtime = datetime.datetime(2005,1,1, hour = 23, tzinfo = ICalendar.utc)
        self.assert_(event.startTime == evtime,
         "startTime not set properly, startTime is %s"
         % event.startTime)

    def DateImportAsAllDay(self):
        format = self.Import(self.repo.view, u'AllDay.ics')
        event = format.findUID('testAllDay')
        self.assert_(event.startTime == datetime.datetime(2005,1,1),
         "startTime not set properly for all day event, startTime is %s"
         % event.startTime)
        self.assert_(event.allDay == True,
         "allDay not set properly for all day event, allDay is %s"
         % event.allDay)
         
    def ItemsToVobject(self):
        """Tests itemsToVObject, which converts Chandler items to vobject."""
        event = Calendar.CalendarEvent(view = self.repo.view)
        event.displayName = u"test"
        event.startTime = datetime.datetime(2010, 1, 1, 10)
        event.endTime = datetime.datetime(2010, 1, 1, 11)        

        cal = ICalendar.itemsToVObject(self.repo.view, [event])

        self.assert_(cal.vevent[0].summary[0].value == "test",
         "summary not set properly, summary is %s"
         % cal.vevent[0].summary[0].value)

        start = event.startTime.replace(tzinfo=ICalendar.localtime)

        self.assert_(cal.vevent[0].dtstart[0].value == start,
         "dtstart not set properly, dtstart is %s"
         % cal.vevent[0].summary[0].value)

        event = Calendar.CalendarEvent(view = self.repo.view)
        event.displayName = u"test2"
        event.startTime = datetime.datetime(2010, 1, 1)
        event.allDay = True        

        cal = ICalendar.itemsToVObject(self.repo.view, [event])

        self.assert_(cal.vevent[0].dtstart[0].value == datetime.date(2010,1,1),
         "dtstart for allDay event not set properly, dtstart is %s"
         % cal.vevent[0].summary[0].value)
         # test bug 3509, all day event duration is off by one
         
    def writeICalendarUnicodeBug3338(self):
        event = Calendar.CalendarEvent(view = self.repo.view)
        event.displayName = u"unicode \u0633\u0644\u0627\u0645"
        event.startTime = datetime.datetime(2010, 1, 1, 10)
        event.endTime = datetime.datetime(2010, 1, 1, 11)

        coll = ListCollection(name="testcollection", parent=self.sandbox)
        coll.add(event)
        filename = u"unicode_export.ics"

        conduit = Sharing.FileSystemConduit(name="conduit", sharePath=u".",
                            shareName=filename, view=self.repo.view)
        format = ICalendar.ICalendarFormat(name="format", view=self.repo.view)
        self.share = Sharing.Share(name="share",contents=coll, conduit=conduit,
                                    format=format, view=self.repo.view)
        if self.share.exists():
            self.share.destroy()
        self.share.create()
        self.share.put()
        cal=vobject.readComponents(file(filename, 'rb')).next()
        self.assertEqual(cal.vevent[0].summary[0].value, event.displayName)
        self.share.destroy()

    def importRecurrence(self):
        format = self.Import(self.repo.view, u'Recurrence.ics')
        event = format.findUID('5B30A574-02A3-11DA-AA66-000A95DA3228')
        third = event.getNextOccurrence().getNextOccurrence()
        self.assertEqual(third.displayName, u'Changed title')
        self.assertEqual(third.recurrenceID, datetime.datetime(2005, 8, 10))
        # while were at it, test bug 3509, all day event duration is off by one
        self.assertEqual(event.duration, datetime.timedelta(0))

    def importRecurrenceWithTimezone(self):
        format = self.Import(self.repo.view, u'RecurrenceWithTimezone.ics')
        event = format.findUID('FF14A660-02A3-11DA-AA66-000A95DA3228')
        third = event.modifications.first()
        # THISANDFUTURE change creates a new event, so there's nothing in
        # event.modifications
        self.assertEqual(third, None)
        #self.assertEqual(third.rruleset.rrules.first().freq, 'daily')
        
    def exportRecurrence(self):
        helper = ICalendar.RecurrenceHelper
        start = datetime.datetime(2005,2,1)
        self.assertEqual(helper.pacificTZ.utcoffset(start),
                         datetime.timedelta(hours=-8))                         
        vevent = vobject.icalendar.RecurringComponent(name='VEVENT')
        vevent.behavior = vobject.icalendar.VEvent
        
        # dateForVObject should take a naive datetime and assume it's in Pacific
        vevent.setDtstart(ICalendar.dateForVObject(start))
        self.assertEqual(vevent.getDtstart().tzinfo, helper.pacificTZ)

        # not creating a RuleSetItem, although it would be required for an item
        ruleItem = RecurrenceRule(None, view=self.repo.view)
        ruleItem.freq = 'daily'
        
        vevent = vevent.transformFromNative()
        helper.addRRule(vevent, ruleItem)
        self.assertEqual(vevent.rrule[0].value, 'FREQ=DAILY')
    
        # addRRule should treat until as being in Pacific time if it has no TZ
        vevent.rrule=[]
        ruleItem.until = datetime.datetime(2005,3,1)
        ruleItem.untilIsDate = False
        helper.addRRule(vevent, ruleItem)
        self.assertEqual(vevent.rrule[0].value,
                         'FREQ=DAILY;UNTIL=20050301T080000Z')
                         
        event = Calendar.CalendarEvent(view = self.repo.view)
        event.displayName = u"blah"
        event.startTime = start
        event.endTime = datetime.datetime(2005,3,1,1)
        
        ruleItem = RecurrenceRule(None, view=self.repo.view)
        ruleItem.until = datetime.datetime(2005,3,1)
        ruleSetItem = RecurrenceRuleSet(None, view=self.repo.view)
        ruleSetItem.addRule(ruleItem)
        event.rruleset = ruleSetItem
        
        vcalendar = ICalendar.itemsToVObject(self.repo.view, [event])
        
        self.assertEqual(vcalendar.vevent[0].dtstart[0].serialize(),
                         'DTSTART;TZID=US/Pacific:20050201T000000\r\n')
        vcalendar.vevent[0] = vcalendar.vevent[0].transformFromNative()
        self.assertEqual(vcalendar.vevent[0].rrule[0].serialize(),
                         'RRULE:FREQ=WEEKLY;UNTIL=20050302T075900Z\r\n')
        
        # move the second occurrence one day later
        nextEvent = event.getNextOccurrence()
        nextEvent.changeThis('startTime', datetime.datetime(2005,2,9))

        vcalendar = ICalendar.itemsToVObject(self.repo.view, [event])
        modified = vcalendar.vevent[1]
        self.assertEqual(modified.dtstart[0].serialize(),
                         'DTSTART;TZID=US/Pacific:20050209T000000\r\n')
        self.assertEqual(modified.contents['recurrence-id'][0].serialize(),
                         'RECURRENCE-ID;TZID=US/Pacific:20050208T000000\r\n')
        
        
        

         
# test import/export unicode

class TimeZoneTestCase(unittest.TestCase):
    
    def getICalTzinfo(self, lines):
        fileobj = cStringIO.StringIO("\r\n".join(lines))
        parsed = tz.tzical(fileobj)

        return parsed.get()
    
    def runConversionTest(self, expectedZone, icalZone):
        dt = datetime.datetime(2004, 10, 11, 13, 22, 21, tzinfo=icalZone)
        convertedZone = ICalendar.convertToICUtzinfo(dt).tzinfo
        self.failUnless(isinstance(convertedZone, ICUtzinfo))
        self.failUnlessEqual(expectedZone, convertedZone)

        dt = datetime.datetime(2004, 4, 11, 13, 9, 56, tzinfo=icalZone)
        convertedZone = ICalendar.convertToICUtzinfo(dt).tzinfo
        self.failUnless(isinstance(convertedZone, ICUtzinfo))
        self.failUnlessEqual(expectedZone, convertedZone)
    
    def testVenezuela(self):
        zone = self.getICalTzinfo([
            "BEGIN:VTIMEZONE",
            "TZID:America/Caracas",
            "LAST-MODIFIED:20050817T235129Z",
            "BEGIN:STANDARD",
            "DTSTART:19321213T204552",
            "TZOFFSETTO:-0430",
            "TZOFFSETFROM:+0000",
            "TZNAME:VET",
            "END:STANDARD",
            "BEGIN:STANDARD",
            "DTSTART:19650101T000000",
            "TZOFFSETTO:-0400",
            "TZOFFSETFROM:-0430",
            "TZNAME:VET",
            "END:STANDARD",
            "END:VTIMEZONE"])
        
        self.runConversionTest(
            ICUtzinfo.getInstance("America/Caracas"),
            zone)
        
    def testAustralia(self):
        
        zone = self.getICalTzinfo([
            "BEGIN:VTIMEZONE",
            "TZID:Australia/Sydney",
            "LAST-MODIFIED:20050817T235129Z",
            "BEGIN:STANDARD",
            "DTSTART:20050326T160000",
            "TZOFFSETTO:+1000",
            "TZOFFSETFROM:+0000",
            "TZNAME:EST",
            "END:STANDARD",
            "BEGIN:DAYLIGHT",
            "DTSTART:20051030T020000",
            "TZOFFSETTO:+1100",
            "TZOFFSETFROM:+1000",
            "TZNAME:EST",
            "END:DAYLIGHT",
            "END:VTIMEZONE"])
        
        self.runConversionTest(
            ICUtzinfo.getInstance("Australia/Sydney"),
            zone)
        
    def testFrance(self):

        zone = self.getICalTzinfo([
            "BEGIN:VTIMEZONE",
            "TZID:Europe/Paris",
            "LAST-MODIFIED:20050817T235129Z",
            "BEGIN:DAYLIGHT",
            "DTSTART:20050327T010000",
            "TZOFFSETTO:+0200",
            "TZOFFSETFROM:+0000",
            "TZNAME:CEST",
            "END:DAYLIGHT",
            "BEGIN:STANDARD",
            "DTSTART:20051030T030000",
            "TZOFFSETTO:+0100",
            "TZOFFSETFROM:+0200",
            "TZNAME:CET",
            "END:STANDARD",
            "END:VTIMEZONE"])

        self.runConversionTest(
            ICUtzinfo.getInstance("Europe/Paris"),
            zone)
        
    def testUS(self):
        zone = self.getICalTzinfo([
            "BEGIN:VTIMEZONE",
            "TZID:US/Pacific",
            "LAST-MODIFIED:20050817T235129Z",
            "BEGIN:DAYLIGHT",
            "DTSTART:20050403T100000",
            "TZOFFSETTO:-0700",
            "TZOFFSETFROM:+0000",
            "TZNAME:PDT",
            "END:DAYLIGHT",
            "BEGIN:STANDARD",
            "DTSTART:20051030T020000",
            "TZOFFSETTO:-0800",
            "TZOFFSETFROM:-0700",
            "TZNAME:PST",
            "END:STANDARD",
            "END:VTIMEZONE"])
        self.runConversionTest(
            ICUtzinfo.getInstance("US/Pacific"),
            zone)

if __name__ == "__main__":
    unittest.main()
