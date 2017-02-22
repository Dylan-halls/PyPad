import gi, subprocess, os
gi.require_version('Gtk', '3.0')
from os.path import basename
from gi.repository import Gtk, GtkSource, Gdk, Pango

class SearchDialog(Gtk.Dialog):

    def __init__(self, parent):
    	  start_iter = text_buffer.get_start_iter()
    	  end_iter = text_buffer.get_end_iter()
    	  text_buffer.remove_tag_by_name("found", start_iter, end_iter)

    	  Gtk.Dialog.__init__(self, "Search", parent, Gtk.DialogFlags.MODAL, buttons=(Gtk.STOCK_FIND, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
    	  box = self.get_content_area()
    	  label = Gtk.Label("Insert text you want to search for:")
    	  box.add(label)

    	  self.entry = Gtk.Entry()
    	  box.add(self.entry)
    	  self.show_all()

class PyApp(Gtk.Window):
	global tab_data, tabs
	tabs = []
	tab_data = {}

	def _run_script(self):
		frame = Gtk.Frame()
		frame.set_size_request(100, 75)
		sc = Gtk.ScrolledWindow(None, None)

		#ctext = GtkSource.View()
		#ctext_buffer = ctext.get_buffer()
		#ctext.show()

		#sc.add(ctext)
		#sc.show()
		#frame.add(sc)
		frame.show()
		vbox.add(frame)

		cmd = ['python', '-u', '/root/Documents/PyPad/pypad.py']

		p = subprocess.Popen(cmd,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)

		for line in iter(p.stdout.readline, b''):
			l = Gtk.Label()
			l.set_text(line.rstrip())
			l.show()
			frame.add(l)

	def _remove_tags(self):
		end = text_buffer.get_end_iter()
		start = text_buffer.get_start_iter()
		text_buffer.remove_tag_by_name("found", start, end)
		print('done')

	def on_search_clicked(self):
		dialog = SearchDialog(self)
		response = dialog.run()
		search_str =  dialog.entry.get_text()
		start_iter =  text_buffer.get_start_iter() 
		found = start_iter.forward_search(search_str,0, None) 
		if found:
		   match_start,match_end = found
		   text_buffer.select_range(match_start,match_end)
		   #text_buffer.remove_tag_by_name("found", match_start, match_end)
		   #tag_found = text_buffer.create_tag(tag_name="found", background="orange")
		   #text_buffer.apply_tag(tag_found, match_start, match_end)

	def _open_file(self):
		global title
		dialog = Gtk.FileChooserDialog("Please choose a file", self, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		dialog.set_size_request(100, 75)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			title = basename(dialog.get_filename())
			path = dialog.get_filename()
			self.add_page('button', title=title, path=path)
			with open(dialog.get_filename(), 'r') as file:
				data = file.read()
				file.close()
				text_buffer.set_text(data)
				dialog.destroy()
		elif response == Gtk.ResponseType.CANCEL:
			print("Cancel clicked")
			dialog.destroy() 

	def _save_file(self):
	   #Get Text From The Window
	   pat = tabs[notebook.get_current_page()]
	   for key,val in tab_data.items():
	   	if key == pat:
	   		print("SAVE -->", key)
	   		print("TEXTBUFFER -->", val)
	   		text_buffer = val
	   		start_iter = text_buffer.get_start_iter()
	   		end_iter = text_buffer.get_end_iter()
	   		file_data = text_buffer.get_text(start_iter, end_iter, True)
	   		file = open(key, 'wb')
	   		print(file_data)
	   		file.write(file_data)
	   		file.close()

	def add_page(self, button, title='Untitled', path=None):
	   global text_buffer, text_box
	   tabs.append(path)
	   frame = Gtk.Frame()
	   frame.set_size_request(100, 75)
	   scw = Gtk.ScrolledWindow(None, None)

	   text_box = GtkSource.View()
	   text_box.set_show_line_numbers(True)
	   text_box.set_auto_indent(True)
	   text_box.set_show_line_marks(True)
	   text_box.get_completion()
	   text_box.show()
	   text_buffer = text_box.get_buffer()
	   bold = text_buffer.create_tag("bold", weight=Pango.Weight.BOLD)
	   start_iter = text_buffer.get_start_iter()
	   end_iter = text_buffer.get_end_iter()
	   text_buffer.apply_tag(bold, start_iter, end_iter)
	   tab_data[path] = text_box.get_buffer()

	   box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
	   Gtk.StyleContext.add_class(box.get_style_context(), "linked")

	   def on_currency_combo_changed(combo):
	       global text
	       text = combo.get_active_text()
	       if text != None:
	           print("Selected: Syntax=%s" % text)
	           text_buffer.set_language(lang_manager.get_language(text))

	   
	   currencies = ["None", "python", "html", "ruby"]
	   currency_combo = Gtk.ComboBoxText()
	   currency_combo.set_entry_text_column(0)
	   currency_combo.connect("changed", on_currency_combo_changed)
	   for currency in currencies:
	       currency_combo.append_text(currency)

	   currency_combo.show()
	   hb.add(currency_combo)
	   hb.pack_start(box)

	   lang_manager = GtkSource.LanguageManager()
	   try:
	      text_buffer.set_language(lang_manager.get_language(text))
	   except: pass

	   def _catch_tab(widget, event):
	      keyval = event.keyval
	      keyval_name = Gdk.keyval_name(keyval)
	      state = event.state
	      ctrl = (state and Gdk.ModifierType.CONTROL_MASK)
	      if ctrl and keyval_name == 's':
	            self._save_file()
	      if ctrl and keyval_name == 'o':
	            self._open_file()
	      if ctrl and keyval_name == 'f':
	      		self.on_search_clicked()
	      if ctrl and keyval_name == 't':
	      		print(tabs[notebook.get_current_page()])
	      		self._remove_tags()

	   self.connect('key_release_event', _catch_tab)

	   def remove_book(button, notebook):
	   	pat = tabs[notebook.get_current_page()]
	   	del tabs[notebook.get_current_page()]
	   	for key,val in tab_data.items():
	   		if key == pat:
	   			print("REMOVE -->", key)
	   			print("TEXTBUFFER -->", val)
	   	#del tab_data[pat]
	   	page = notebook.get_current_page()
	   	notebook.remove_page(page)
	   	notebook.queue_draw_area(0,0,-1,-1)
	   	currency_combo.hide()
	   	print(tabs)
	   	print(tab_data)

	   tab = Gtk.HBox()
	   label = Gtk.Label(title)
	   label.show()
	   tab.pack_start(label, False, False, 0)
	   close_tab = Gtk.ToolButton(Gtk.STOCK_CLOSE)
	   close_tab.connect('clicked', remove_book, notebook)
	   close_tab.show()
	   tab.pack_start(close_tab, False, False, 5)

	   scw.add(text_box)
	   scw.show()
	   frame.add(scw)
	   frame.show()

	   notebook.append_page(frame, tab)
	   print(tabs)
	   print(tab_data)


	def __init__(self):
	   global notebook, hb, console_box, vbox
	   super(PyApp, self).__init__()
	   self.set_title("PyPad")
	   self.set_size_request(1000,600)
	   vbox = Gtk.VBox(False, 5)
	   console_box = Gtk.VBox()
	   notebook = Gtk.Notebook()
	   notebook.set_scrollable(True)
	   #notebook.set_tab_pos(Gtk.POS_TOP)
	   vbox.add(notebook)
	   notebook.show()

	   hb = Gtk.HeaderBar()
	   hb.set_show_close_button(True)
	   hb.props.title = "PyPad"
	   self.set_titlebar(hb)

	   button = Gtk.Button()

	   save = Gtk.ToolButton(Gtk.STOCK_ADD)
	   save.connect("clicked", self.add_page)
	   
	   hb.add(save)

	   def _catch_tab(widget, event):
	      keyval = event.keyval
	      keyval_name = Gdk.keyval_name(keyval)
	      state = event.state
	      ctrl = (state and Gdk.ModifierType.CONTROL_MASK)
	      if ctrl and keyval_name == 's':
	            self._save_file()
	      if ctrl and keyval_name == 'o':
	            self._open_file()
	      if ctrl and keyval_name == 'f':
	      		self.on_search_clicked()
	      if ctrl and keyval_name == 't':
	      		print(tabs[notebook.get_current_page()])
	      		self._remove_tags()
	      if ctrl and keyval_name == 'b':
	      		self._run_script()

	   self.connect('key_release_event', _catch_tab)
	   self.add(vbox)
	   self.connect("destroy", Gtk.main_quit)
	   self.show_all()

if __name__ == '__main__':
	PyApp()
	Gtk.main()