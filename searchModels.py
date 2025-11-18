#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from xml.etree.ElementPath import prepare_descendant

import wx
from Gui import SearchFrame
from pathlib import Path
from spice_search import get_folders, get_files as gf, get_models as gm
import tomli
import tomli_w




from spice_search.get_models import get_models

# todo: make decoding selection and add to file decoding
# todo: remove print statements
# todo: save result as .lib or .cir file (now cntrl-a, ctrl-c/v)
# todo: open file in editor with encoding options (also from search menu)
# todo: open edit with proper decoding
# todo: make local menu specific

configuration_file = "searchModels.toml"

initial_decode_priority = ['utf-8', 'ISO-8859-15', 'SHIFT_JIS']

#search parameters
# todo: transfer patterns to config
search_subckt = {
    'model': '.SUBCKT',  # name to search for
    'model_pos': 0,      # which word for the model (after a split)
    'name_pos':  1,       # which word is the name of the model
    'model_end': '.ENDS',
    'continuation': True,  # .ENDS is the end
    'max_comment_count' : 20  # comments before the subckt is found
}

search_model = {
    'model': '.MODEL',  # name to search for
    'model_pos': 2,      # which word for the model (after a split)
    'name_pos':  1,      # which word is the name of the model
    'model_end': '',
    'continuation': False,  # with '+' or //
    'max_comment_count': 2  # comments before the .model is found
}


class MyFrame(SearchFrame):
    def __init__(self, *args, **kwds):
        SearchFrame.__init__(self, *args, **kwds)
        # if required, insert more initialization code here and create data structures
        self.config_path = Path(configuration_file).resolve()
        if self.config_path.exists():
            self.config = tomli.load(open(self.config_path, "rb"))
        else:
            self.config = dict()
            self.config['comment'] = 'searchModels a searcher for spice models'
        self.text_ctrl_search_folder.SetValue(self.config.get('search_folder', ''))
        self.text_ctrl_destination_folder.SetValue(self.config.get('destination_folder', ''))
        if 'check_recursive' in self.config:
            self.checkbox_recursive.SetValue(self.config['check_recursive'])
        if 'check_model' in self.config:
            self.checkbox_model.SetValue(self.config['check_model'])
        if 'check_subckt' in self.config:
            self.checkbox_subckt.SetValue(self.config['check_subckt'])

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSearchSelected, self.panel_list_search.list)
        #prepare search menu
        if not 'history_length'  in self.config:
            self.config['history_length'] = 10
        self.history_length = int(self.config.get('history_length', 10))
        self.text_ctrl_history_length.SetValue(str(self.history_length))
        self.hist_ref = {}
        for index in range(self.history_length):
            self.hist_ref[index] = wx.NewIdRef()
            self.Bind(wx.EVT_MENU, self.on_search_history, id=self.hist_ref[index])

        self.history = self.config.get('history', [])
        if len(self.history) > self.history_length:
            self.history = self.history[:self.history_length]
        self.search_ctrl_1.SetMenu(self.make_menu())

        # set file encoding
        if not 'decode_priority' in self.config:
            self.config['decode_priority'] = initial_decode_priority
        self.decode_priority = self.config['decode_priority']
        self.list_box_priority.Set(self.decode_priority)


    def save_config(self):
        with open(self.config_path, "wb") as f:
            tomli_w.dump(self.config, f)

    def on_search_history(self, event):
        id = event.GetId()
        index = [ k for k, v in self.hist_ref.items() if v == id][0]
        if index < len(self.history):
            self.search_ctrl_1.SetValue(self.history[index])


    def on_search(self, event):
        search_string = self.search_ctrl_1.GetValue().upper()
        print(f' searching for: {search_string}')
        print(f'searching in: {self.text_ctrl_search_folder.Value}')

        path = Path(self.text_ctrl_search_folder.Value).absolute().resolve(strict=False)
        if self.text_ctrl_search_folder.Value == '':
            dlg = wx.MessageDialog(self, 'Missing search folder in configuration',
                                   'Warning',
                                   wx.OK | wx.ICON_WARNING
                                   # wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                   )
            dlg.ShowModal()
            dlg.Destroy()
        elif not path.exists():
            dlg = wx.MessageDialog(self, f'path: {self.text_ctrl_search_folder.Value} is not a valid folder',
                                   'Warning',
                                   wx.OK | wx.ICON_WARNING
                                   # wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                   )
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.log(' start searching in ...')
            if not path.is_dir():
                path = path.parent
            self.log(str(path))
            # update history menu
            if search_string != "" and ((self.history_length) == 0 or search_string != self.history[0]):
                self.history.insert(0, search_string)
                if len(self.history) > self.history_length:
                    self.history.pop(-1)
                self.search_ctrl_1.SetMenu(self.make_menu())
                self.config['history'] = self.history
                self.save_config()


            # todo: report models on wrong position
            # todo: simplify checked items combination with new items
            folders = [ str(d) for d in Path(path).glob('**') if d.is_dir]
            present_folder_list = self.panel_list_folders.GetList()
            present_folders = [ v[0] for k,v in present_folder_list.items()]
            new_folders = [ f for f in folders if f not in present_folders]
            for f in new_folders:
                index = len(present_folder_list) + 1
                present_folder_list[index] = [str(f), 0, 0, True]
            self.panel_list_folders.PopulateList(present_folder_list)
            self.text_ctrl_number_of_folders.SetValue(str(len(present_folder_list)))

            # present_folder_list = self.panel_list_folders.GetList()
            itemchecked = self.panel_list_folders.getChecked()
            search_folders = { k: present_folder_list[k] for k in itemchecked}


            present_file_list = self.panel_list_files.GetList()
            present_extensions = self.panel_list_extensions.GetList()
            current_files, extensions = gf.getFiles(search_folders) # get all files based on folders
            self.panel_list_folders.PopulateList() # populate after file count update
            # update extensions
            skip_extensions = [ v[0] for k,v in present_extensions.items()]
            for k, v in extensions.items():
                if not v[0] in skip_extensions:
                    index = len(present_extensions) + 1
                    present_extensions[index] = v
            self.panel_list_extensions.PopulateList(present_extensions)
            self.text_ctrl_number_of_extensions.SetValue(str(len(present_extensions)))

            # update files
            skip_files = [ v[0] for k,v in present_file_list.items()]
            for k, v in current_files.items():
                if not v[0] in skip_files:
                    index = len(present_file_list) + 1
                    present_file_list[index] = v
            self.panel_list_files.PopulateList(present_file_list)
            self.text_ctrl_number_of_files.SetValue(str(len(present_file_list)))

            # get checked files
            itemschecked = self.panel_list_files.getChecked()
            search_files = {k: present_file_list[k] for k in itemschecked}
            # filter on extensions
            extensions_checked_keys = self.panel_list_extensions.getChecked()
            extensions_checked = [ v[0] for k, v in present_extensions.items() if k in extensions_checked_keys]
            search_files = { k: v for k, v in search_files.items() if Path(v[0]).suffix in extensions_checked }

            recursive = self.checkbox_recursive.Value
            all_result_list = {}
            # get subckt results
            if self.checkbox_subckt.Value:
                for k, v in search_files.items():
                    # print(str(v[0]))
                    for enc in self.decode_priority:
                        found = False
                        try:
                            all_result_list, model_count, error_list = gm.get_models(v[0], all_result_list, recursive, enc, **search_subckt)
                            v[1] += model_count
                            for err in error_list:
                                self.log(err)
                            found = True
                        except  UnicodeDecodeError:

                             # error_list.append
                            print(f' unicode error {enc:10} in file: {str(v[0])}')
                        if found:
                            break

                # current_models = self.panel_list_models.GetList()
                # skip_models = [ v[0] for k,v in current_models.items()]
                # for k, v in all_result_list.items():
                #     if not v[0] in skip_models:
                #         index = len(current_models) + 1
                #         current_models[index] = v
                # self.panel_list_models.PopulateList(current_models)

            # get .models result
            if self.checkbox_model.Value:
                for k, v in search_files.items():
                    for enc in self.decode_priority:
                        found = False
                        try:
                            all_result_list, model_count, error_list = gm.get_models(v[0], all_result_list, recursive, enc, **search_model)
                            v[1] += model_count
                            found = True
                            for err in error_list:
                                self.log(err)
                        except  UnicodeDecodeError:

                             # error_list.append
                            print(f' unicode error {enc} in file: {str(v[0])}')
                        if found:
                            break

                # current_models = self.panel_list_models.GetList()
                # skip_models = [ v[0] for k,v in current_models.items()]
                # for k, v in all_result_list.items():
                #     if not v[0] in skip_models:
                #         index = len(current_models) + 1
                #         current_models[index] = v
                # self.panel_list_models.PopulateList(current_models)
            self.panel_list_files.PopulateList(present_file_list) # update the count
            self.text_ctrl_number_of_files.SetValue(str(len(present_file_list)))

            # update model list
            present_model_list = self.panel_list_models.GetList()
            # present_model_list_models =
            for k, value in all_result_list.items():
                if not value[1] in [ v[0] for k, v in present_model_list.items()]:
                    index = len(present_model_list) + 1
                    present_model_list[index] = [ value[1] , 0 , True]  # model, count, checked
            # update model count
            for k, v in present_model_list.items():
                #clear count
                present_model_list[k][1] = 0
                # look for model
                for k2, v2 in all_result_list.items():
                    if v[0] == v2[1]:
                        present_model_list[k][1] += 1


            self.panel_list_models.PopulateList(present_model_list)
            self.text_ctrl_number_of_models.SetValue(str(len(present_model_list)))

            # filter result and build list
            # get used models
            selected_items = self.panel_list_models.getChecked()
            selected_models = [ v[0] for k,v in present_model_list.items() if k in selected_items ]
            index = 1
            result_list = {}
            for k, v in all_result_list.items():
                if v[1] in selected_models:
                    if search_string in v[0].upper():
                        result_list[index] = v
                        index += 1

            self.panel_list_search.PopulateList(result_list)
            self.text_ctrl_search_count.SetValue((str(len(result_list))))

    def on_clear(self, event):
        self.panel_list_folders.ClearList()
        self.text_ctrl_number_of_folders.SetValue('0')
        self.panel_list_files.ClearList()
        self.text_ctrl_number_of_files.SetValue('0')
        self.panel_list_models.ClearList()
        self.text_ctrl_number_of_models.SetValue('0')
        self.panel_list_search.ClearList()
        # self.text_ctrl_number_of_folders.SetValue('0')
        self.panel_list_extensions.ClearList()
        self.text_ctrl_number_of_extensions.SetValue('0')
        self.text_ctrl_log.SetValue('')

    def OnSearchSelected(self, event):
        item = event.GetItem()
        print("OnItemSelected: %d" % event.Index)
        # get all:
        indices = []
        ind = self.panel_list_search.list.GetFirstSelected()
        while ind > 0:
            indices.append(ind)
            ind = self.panel_list_search.list.GetNextSelected(ind)
        print(f'selected {str(indices)}')
        model_body =[]
        for i in indices:
            index = self.panel_list_search.getOrgIndex(i)
            selected = self.panel_list_search.itemDataMap[index]
            if selected[1].upper() == search_subckt['model']:
                args = search_subckt
            else:
                args = search_model
            filepath = selected[2]
            string = selected[0]
            model_body += gm.get_model_body(filepath, string, True, **args)
            print(model_body)
        self.text_ctrl_content.SetValue(''.join(model_body))

    def on_checkbox_recursive(self, event):
        checked = self.checkbox_recursive.Value
        self.config['check_recursive'] = checked
        self.save_config()

    def on_checkbox_model(self, event):
        checked = self.checkbox_model.Value
        self.config['check_model'] = checked
        self.save_config()

    def on_checkbox_subckt(self, event):
        checked = self.checkbox_subckt.Value
        self.config['check_subckt'] = checked
        self.save_config()

    def on_text_ctrl_search_folder_enter(self, event):
        search_path = Path(self.text_ctrl_search_folder.Value).resolve()
        self.config['search_folder'] = str(search_path)
        self.save_config()


    def on_search_folder(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE,
                           defaultPath=self.text_ctrl_search_folder.Value
                           # | wx.DD_DIR_MUST_EXIST
                           # | wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            search_path = str(Path(dlg.GetPath()).resolve())
            self.text_ctrl_search_folder.SetValue(search_path)
            self.config['search_folder'] = search_path
            self.save_config()

    def on_text_ctrl_destination_folder_enter(self, event):
        search_path = Path(self.text_ctrl_destination_folder.Value).resolve()
        self.config['destination_folder'] = str(search_path)
        self.save_config()

    def on_clear_model_list(self, event):
        self.panel_list_models.ClearList()

    def on_clear_extension_list(self, event):
        self.panel_list_extensions.ClearList()

    def on_clear_files_list(self, event):
        self.panel_list_files.ClearList()

    def on_clear_list_folders(self, event):
        self.panel_list_folders.ClearList()

    def on_destination_folder(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE,
                           defaultPath=self.text_ctrl_destination_folder.Value
                           # | wx.DD_DIR_MUST_EXIST
                           # | wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            search_path = str(Path(dlg.GetPath()).resolve())
            self.text_ctrl_destination_folder.SetValue(search_path)
            self.config['destination_folder'] = search_path
            self.save_config()

    def on_text_ctrl_history_length(self, event):
        self.config['history_length'] = str(self.text_ctrl_history_length.Value)
        self.save_config()

    # def on_add(self, event):
    #     self.panel_list_folders.AppendList({1: folder_data[2]})

    def on_button_priority_up(self, event):
        selected = self.list_box_priority.GetSelection()
        if selected == wx.NOT_FOUND:
            selected = 0
            self.list_box_priority.SetSelection(selected)
        if selected > 0 and selected < len(self.decode_priority):
            self.decode_priority[selected-1], self.decode_priority[selected] = (self.decode_priority[selected],
                                                                                self.decode_priority[selected-1])
            self.list_box_priority.Set(self.decode_priority)
            self.list_box_priority.SetSelection(selected-1)
            self.save_config()


    def on_button_priority_down(self, event):
        selected = self.list_box_priority.GetSelection()
        if selected == wx.NOT_FOUND:
            selected = 0
            self.list_box_priority.SetSelection(selected)
        if selected >= 0 and selected < len(self.decode_priority)-1:
            self.decode_priority[selected+1], self.decode_priority[selected] = (self.decode_priority[selected],
                                                                                self.decode_priority[selected+1])
            self.list_box_priority.Set(self.decode_priority)
            self.list_box_priority.SetSelection(selected+1)
            self.config['decode_priority'] = self.decode_priority
            self.save_config()




    def make_menu(self):
        menu = wx.Menu()
        item = menu.Append(-1, "Recent Searches...")
        item.Enable(False)
        for index in range(len(self.history)):
            menu.Append(self.hist_ref[index], self.history[index])
        return menu

    def log(self, text, str_end='\n'):
        """logging to window"""
        self.text_ctrl_log.write(text+str_end)


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()

