#!/usr/bin/env python


import sys
from os.path import exists

import wx
import wx.lib.mixins.listctrl as listmix

import images

#---------------------------------------------------------------------------
class Log():
    def init(self):
        pass
    def WriteText(self,txt):
        print(txt)
log = Log()
musicheaders = ['Artist', 'Title', 'Genre']
musicdata = {
1 : ("Bad English", "The Price Of Love", "Rock"),
2 : ("DNA featuring Suzanne Vega", "Tom's Diner", "Rock"),
3 : ("George Michael", "Praying For Time", "Rock"),
4 : ("Gloria Estefan", "Here We Are", "Rock"),
5 : ("Linda Ronstadt", "Don't Know Much", "Rock"),
6 : ("Michael Bolton", "How Am I Supposed To Live Without You", "Blues"),
7 : ("Paul Young", "Oh Girl", "Rock"),
8 : ("Paula Abdul", "Opposites Attract", "Rock"),
9 : ("Richard Marx", "Should've Known Better", "Rock"),
10: ("Rod Stewart", "Forever Young", "Rock"),
11: ("Roxette", "Dangerous", "Rock"),
12: ("Sheena Easton", "The Lover In Me", "Rock"),
13: ("Sinead O'Connor", "Nothing Compares 2 U", "Rock"),
14: ("Stevie B.", "Because I Love You", "Rock"),
15: ("Taylor Dayne", "Love Will Lead You Back", "Rock"),
16: ("The Bangles", "Eternal Flame", "Rock"),
17: ("Wilson Phillips", "Release Me", "Rock"),
18: ("Billy Joel", "Blonde Over Blue", "Rock"),
19: ("Billy Joel", "Famous Last Words", "Rock"),
20: ("Janet Jackson", "State Of The World", "Rock"),
21: ("Janet Jackson", "The Knowledge", "Rock"),
22: ("Spyro Gyra", "End of Romanticism", "Jazz"),
23: ("Spyro Gyra", "Heliopolis", "Jazz"),
24: ("Spyro Gyra", "Jubilee", "Jazz"),
25: ("Spyro Gyra", "Little Linda", "Jazz"),
26: ("Spyro Gyra", "Morning Dance", "Jazz"),
27: ("Spyro Gyra", "Song for Lorraine", "Jazz"),
28: ("Yes", "Owner Of A Lonely Heart", "Rock"),
29: ("Yes", "Rhythm Of Love", "Rock"),
30: ("Billy Joel", "Lullabye (Goodnight, My Angel)", "Rock"),
31: ("Billy Joel", "The River Of Dreams", "Rock"),
32: ("Billy Joel", "Two Thousand Years", "Rock"),
33: ("Janet Jackson", "Alright", "Rock"),
34: ("Janet Jackson", "Black Cat", "Rock"),
35: ("Janet Jackson", "Come Back To Me", "Rock"),
36: ("Janet Jackson", "Escapade", "Rock"),
37: ("Janet Jackson", "Love Will Never Do (Without You)", "Rock"),
38: ("Janet Jackson", "Miss You Much", "Rock"),
39: ("Janet Jackson", "Rhythm Nation", "Rock"),
40: ("Cusco", "Dream Catcher", "New Age"),
41: ("Cusco", "Geronimos Laughter", "New Age"),
42: ("Cusco", "Ghost Dance", "New Age"),
43: ("Blue Man Group", "Drumbone", "New Age"),
44: ("Blue Man Group", "Endless Column", "New Age"),
45: ("Blue Man Group", "Klein Mandelbrot", "New Age"),
46: ("Kenny G", "Silhouette", "Jazz"),
47: ("Sade", "Smooth Operator", "Jazz"),
48: ("David Arkenstone", "Papillon (On The Wings Of The Butterfly)", "New Age"),
49: ("David Arkenstone", "Stepping Stars", "New Age"),
50: ("David Arkenstone", "Carnation Lily Lily Rose", "New Age"),
51: ("David Lanz", "Behind The Waterfall", "New Age"),
52: ("David Lanz", "Cristofori's Dream", "New Age"),
53: ("David Lanz", "Heartsounds", "New Age"),
54: ("David Lanz", "Leaves on the Seine", "New Age"),
}
for k, v in musicdata.items():
    if k in [3, 5, 10]:
        musicdata[k] = list(v) + [False]
    else:
        musicdata[k] = list(v) + [True]
musicdata2 = {
1 : ("Bad English", "The Price Of Love", "Rock"),
2 : ("DNA featuring Suzanne Vega", "Tom's Diner", "Rock"),
3 : ("George Michael", "Praying For Time", "Rock"),
4 : ("Gloria Estefan", "Here We Are", "Rock"),
5 : ("Linda Ronstadt", "Don't Know Much", "Rock")
}

for k, v in musicdata2.items():
    if k == 3:
        musicdata2[k] = list(v) + [False]
    else:
        musicdata2[k] = list(v) + [True]


folder_data2 = {
    4: ('/home/jan/local/home/jan/development/cad/KiCad-Spice-Library-master/Scripts/__pycache__', 0, 3, True)
}

#---------------------------------------------------------------------------

class TestListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class NbListCtrlPanel(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent, headers, log):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        self.log = log
        tID = wx.NewIdRef()

        sizer = wx.BoxSizer(wx.VERTICAL)

        if wx.Platform == "__WXMAC__" and \
               hasattr(wx.GetApp().GetTopWindow(), "LoadDemo"):
            self.useNative = wx.CheckBox(self, -1, "Use native listctrl")
            self.useNative.SetValue(
                not wx.SystemOptions.GetOptionInt("mac.listctrl.always_use_generic") )
            self.Bind(wx.EVT_CHECKBOX, self.OnUseNative, self.useNative)
            sizer.Add(self.useNative, 0, wx.ALL | wx.ALIGN_RIGHT, 4)

        self.headers = headers
        self.il = wx.ImageList(16, 16)
        self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
        self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())

        self.list = TestListCtrl(self, tID,
                                 style=wx.LC_REPORT
                                 #| wx.BORDER_SUNKEN
                                 | wx.BORDER_NONE
                                 | wx.LC_EDIT_LABELS
                                 #| wx.LC_SORT_ASCENDING    # disabling initial auto sort gives a
                                 #| wx.LC_NO_HEADER         # better illustration of col-click sorting
                                 #| wx.LC_VRULES
                                 #| wx.LC_HRULES
                                 #| wx.LC_SINGLE_SEL
                                 )

        self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        sizer.Add(self.list, 1, wx.EXPAND)
        self.list.EnableCheckBoxes(enable=True)

        self.itemDataMap = dict()
        self.list_is_empty = True

        # self.PopulateList(list_dict)

        # Now that the list exists we can init the other base class,
        # see wx/lib/mixins/listctrl.py

        listmix.ColumnSorterMixin.__init__(self, len(headers))
        #self.SortListItems(0, True)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        # self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
        self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnItemDelete, self.list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
        self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick, self.list)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self.list)
        self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColEndDrag, self.list)
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.list)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndEdit, self.list)
        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self.OnCheck, self.list)
        self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.OnUnCheck, self.list)

        self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        # for wxMSW
        self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        self.list.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

    def OnUseNative(self, event):
        wx.SystemOptions.SetOption("mac.listctrl.always_use_generic", not event.IsChecked())
        wx.GetApp().GetTopWindow().LoadDemo("ListCtrl")

    def UpdateListItem(self, data_list):
        """updates the list, search trough list for first item and updates if value not None
        """

        if self.list_is_empty:
            return
        for k, v  in self.itemDataMap.items():
            if v[0] == data_list[0]:
                for i in range(1,min(len(data_list), len(v))):
                    if data_list[i] is not None:
                        v[i] = data_list[i]
        # todo: update ineff code (or remove function)
        items = self.itemDataMap.items()
        for key, data in items:
            index = self.list.InsertItem(self.list.GetItemCount(), data[0])
            # self.list.CheckItem(item=index, check=checked)
            for ind in range(1, len(self.headers)):
                self.list.SetItem(index, ind, str(data[ind]))
            self.list.SetItemData(index, key)

    def getOrgIndex(self, list_index):
        """after sorting th index of the list does not correspond to the original
        so we retrieve the items and look for the key """
        t1 = [self.list.GetItemText(list_index)]
        for i in range(1, len(self.headers)):
            t1.append(self.getColumnText(list_index, i))

        index = 0
        found = False
        for k, v in self.itemDataMap.items():
            if v[0] == t1[0]:
                found = True
                for i in range(len(t1)):
                    if str(v[i]) != str(t1[i]):
                        found = False
            if found:
                index = k
                break
        return index


    def GetList(self):
        return {} if self.list_is_empty else self.itemDataMap

    def getChecked(self):
        itemschecked = [ k for k, v in self.itemDataMap.items() if v[-1]]

        return itemschecked


    def AppendList(self, data, checked=False):
        """append one item to the item list only, call populate to update screen"""

        if self.list_is_empty:
            self.itemDataMap = { 1: data}
        else:
            index = max(self.itemDataMap) + 1
            self.itemDataMap[index] = data

    def PopulateList(self, list_dict=None, checked=True):
        self.ClearList()
        if list_dict is not None:
            self.itemDataMap = list_dict

        # for index in self.itemDataMap: # make all str
        #     self.itemDataMap[index] = [ str(a) for a in self.itemDataMap[index][:-1] ]

        for ind, hdr in enumerate(self.headers):
            self.list.InsertColumn(ind, hdr)
        items = self.itemDataMap.items()
        for key, data in items:
            index = self.list.InsertItem(self.list.GetItemCount(), data[0])
            for ind in range(1, len(self.headers)):
                self.list.SetItem(index, ind, str(data[ind]))
            self.list.CheckItem(item=index, check=data[-1])
            self.list.SetItemData(index, key)

        for ind in range(len(self.headers)):
            if ind == 0:
                self.list.SetColumnWidth(ind, wx.LIST_AUTOSIZE)
            else:
                self.list.SetColumnWidth(ind, wx.LIST_AUTOSIZE_USEHEADER )
        # self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        # self.list.SetColumnWidth(2, 100)
        listmix.ColumnSorterMixin.__init__(self, len(self.headers))

        # show how to select an item
        # self.list.SetItemState(5, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

        # show how to change the colour of a couple items
        # item = self.list.GetItem(1)
        # item.SetTextColour(wx.BLUE)
        # self.list.SetItem(item)
        # item = self.list.GetItem(4)
        # item.SetTextColour(wx.RED)
        # self.list.SetItem(item)
        # itemcount = self.list.GetItemCount()
        # [self.list.CheckItem(item=i, check=True) for i in range(itemcount)]


        self.currentItem = 0
        self.list_is_empty = False

    def ClearList(self):
        self.list.ClearAll()
        self.list_is_empty = True

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.list

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

    def OnRightDown(self, event):
        x = event.GetX()
        y = event.GetY()
        self.log.WriteText("x, y = %s\n" % str((x, y)))
        item, flags = self.list.HitTest((x, y))

        if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
            self.list.Select(item)

        event.Skip()

    def getColumnText(self, index, col):
        item = self.list.GetItem(index, col)
        return item.GetText()

    def OnItemSelected(self, event):
        ##print(event.GetItem().GetTextColour())
        self.currentItem = event.Index
        self.log.WriteText("OnItemSelected: %s, %s, %s, %s\n" %
                           (self.currentItem,
                            self.list.GetItemText(self.currentItem),
                            self.getColumnText(self.currentItem, 1),
                            self.getColumnText(self.currentItem, 2)))


        event.Skip()

    def OnItemDeselected(self, event):
        item = event.GetItem()
        self.log.WriteText("OnItemDeselected: %d" % event.Index)

        # Show how to reselect something we don't want deselected
        if event.Index == 11:
            wx.CallAfter(self.list.SetItemState, 11, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

    def OnItemActivated(self, event):
        self.currentItem = event.Index
        self.log.WriteText("OnItemActivated: %s\nTopItem: %s" %
                           (self.list.GetItemText(self.currentItem), self.list.GetTopItem()))

    def OnBeginEdit(self, event):
        self.log.WriteText("OnBeginEdit")
        event.Allow()

    def OnEndEdit(self, event):
        self.log.WriteText("OnEndEdit: " + event.GetText())
        event.Allow()

    def OnCheck(self, event):
        if not self.list_is_empty:
            index = self.getOrgIndex(event.Index)
            # print(f'check on item {event.Index+1 } ')
            self.itemDataMap[index][-1] = True

    def OnUnCheck(self, event):
        if not self.list_is_empty:
            index = self.getOrgIndex(event.Index)
            # print(f'check on item {event.Index+1 } ')
            self.itemDataMap[index][-1] = False

    def OnItemDelete(self, event):
        self.log.WriteText("OnItemDelete\n")

    def OnColClick(self, event):
        self.log.WriteText("OnColClick: %d\n" % event.GetColumn())
        event.Skip()

    def OnColRightClick(self, event):
        item = self.list.GetColumn(event.GetColumn())
        self.log.WriteText("OnColRightClick: %d %s\n" %
                           (event.GetColumn(), (item.GetText(), item.GetAlign(),
                                                item.GetWidth(), item.GetImage())))
        if self.list.HasColumnOrderSupport():
            self.log.WriteText("OnColRightClick: column order: %d\n" %
                               self.list.GetColumnOrder(event.GetColumn()))

    def OnColBeginDrag(self, event):
        self.log.WriteText("OnColBeginDrag\n")
        ## Show how to not allow a column to be resized
        #if event.GetColumn() == 0:
        #    event.Veto()

    def OnColDragging(self, event):
        self.log.WriteText("OnColDragging\n")

    def OnColEndDrag(self, event):
        self.log.WriteText("OnColEndDrag\n")

    def OnCheckAllBoxes(self, event):
        itemcount = self.list.GetItemCount()
        [self.list.CheckItem(item=i, check=True) for i in range(itemcount)]
        self.log.WriteText("OnCheckAllBoxes\n")

    def OnUnCheckAllBoxes(self, event):
        itemcount = self.list.GetItemCount()
        [self.list.CheckItem(item=i, check=False) for i in range(itemcount)]
        self.log.WriteText("OnUnCheckAllBoxes\n")

    def OnGetItemsChecked(self, event):
        itemcount = self.list.GetItemCount()
        itemschecked = [i for i in range(itemcount) if self.list.IsItemChecked(item=i)]
        self.log.WriteText("OnGetItemsChecked: %s \n" % itemschecked)

    def OnDoubleClick(self, event):
        self.log.WriteText("OnDoubleClick item %s\n" % self.list.GetItemText(self.currentItem))
        event.Skip()

    def OnRightClick(self, event):
        self.log.WriteText("OnRightClick %s\n" % self.list.GetItemText(self.currentItem))

        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewIdRef()
            self.popupID2 = wx.NewIdRef()
            self.popupID3 = wx.NewIdRef()
            self.popupID4 = wx.NewIdRef()
            self.popupID5 = wx.NewIdRef()
            self.popupID6 = wx.NewIdRef()
            self.popupID7 = wx.NewIdRef()
            self.popupID8 = wx.NewIdRef()
            self.popupID9 = wx.NewIdRef()

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)
            self.Bind(wx.EVT_MENU, self.OnCheckAllBoxes, id=self.popupID7)
            self.Bind(wx.EVT_MENU, self.OnUnCheckAllBoxes, id=self.popupID8)
            self.Bind(wx.EVT_MENU, self.OnGetItemsChecked, id=self.popupID9)

        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID1, "FindItem tests")
        menu.Append(self.popupID2, "Iterate Selected")
        menu.Append(self.popupID3, "ClearAll and repopulate")
        menu.Append(self.popupID4, "DeleteAllItems")
        menu.Append(self.popupID5, "GetItem")
        menu.Append(self.popupID6, "Edit")
        menu.Append(self.popupID7, "Check All Boxes")
        menu.Append(self.popupID8, "UnCheck All Boxes")
        menu.Append(self.popupID9, "Get Checked Items")

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, event):
        self.log.WriteText("Popup one\n")
        print("FindItem:", self.list.FindItem(-1, "Roxette"))
        print("FindItemData:", self.list.FindItemData(-1, 11))

    def OnPopupTwo(self, event):
        self.log.WriteText("Selected items:\n")
        index = self.list.GetFirstSelected()

        while index != -1:
            self.log.WriteText("      %s: %s\n" % (self.list.GetItemText(index),
                                                   self.getColumnText(index, 1)))
            index = self.list.GetNextSelected(index)

    def OnPopupThree(self, event):
        self.log.WriteText("Popup three\n")
        # self.list.ClearAll()
        # wx.CallAfter(self.AppendList, folder_data2, True)

    def OnPopupFour(self, event):
        self.list.DeleteAllItems()

    def OnPopupFive(self, event):
        item = self.list.GetItem(self.currentItem)
        self.log.WriteText("Text:%s, Id:%s, Data:%s" %(item.Text,
                                                       item.Id,
                                                       self.list.GetItemData(self.currentItem)))

    def OnPopupSix(self, event):
        self.list.EditLabel(self.currentItem)


# --------------------------------------------------------------------
class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        global log
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((731, 532))
        self.SetTitle("frame")
        self.log = log
        self.active = False
        self.panel = NbListCtrlPanel(self, musicheaders, log)


    def add_list(self, datalist, headers):

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.panel, wx.EXPAND, 0)
        self.panel.PopulateList(datalist)

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        wx.CallLater(2000, self.frame.add_list, musicdata, musicheaders)
        wx.CallLater(6000, self.frame.add_list, musicdata2, musicheaders)
        return True

# end of class MyApp

if __name__ == "__main__":

    app = MyApp(0)
    app.MainLoop()
