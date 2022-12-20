import tkinter   as tk
import mss
from pynput.mouse import Listener,Controller
import numpy as np
from PIL import Image, ImageTk
sct = mss.mss()
mouse = Controller()
def make_dynamic(widget,uniform = False ,rows = None,columns = None):

	col_count,row_count = widget.grid_size()
	if rows == None:
		rows = range(row_count)
	for i in rows:
		widget.grid_rowconfigure(i, weight = 1, uniform = uniform)

	if columns  == None:
		columns = range(col_count)
	for i in columns:
		widget.grid_columnconfigure(i, weight = 1, uniform = uniform)

def _create_circle(self, x, y, r, **kwargs):
	return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle


def change_position(root_variable,x,y):
	root_variable.geometry('+{}+{}'.format(x,y))

def RGB_to_HEX(rgb_pixel):
	return '#%02x%02x%02x' % rgb_pixel
def BGR_to_RGB(bgr_pixel):
	return bgr_pixel[:,:,::-1]

def get_pix(x,y,width=1,height = 1):
	monitor = {"top": y, "left": x, "width": width, "height": height }
	img_array = np.array(sct.grab(monitor))
	img_array = BGR_to_RGB( img_array[:,:,:-1]) 
	pix = tuple(img_array[0,0] )
	#hexx_value = '#%02x%02x%02x' % pix
	return pix

class ResizingCanvas(tk.Canvas):
    def __init__(self,parent,**kwargs):
        tk.Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)
def get_center(widget):
	return root.winfo_width()//2, root.winfo_height()//2

class PickerWindow:
	transparent_color= (134, 126, 54)
	transparent_color_backup = (12, 66, 176)
	maginfier_on = False
	canvas_img = None
	def __init__(self, root,callback = lambda *args:None ):
		root.overrideredirect(True)
		#root.attributes('-alpha',transparency)
		#root.lift()
		root.wm_attributes("-topmost", True)
		root.config(cursor = 'cross')
		#root.wm_attributes("-disabled", True)
		#root.configure(bg = 'green')
		
		content = tk.Frame(root)

		if content:

			canvas = ResizingCanvas(content, width=210, height=210, borderwidth=0, highlightthickness=0)  
			color_circle = canvas.create_circle(105, 105, 90, fill="red", outline="#DDD", width=5)
			transparent_circle = canvas.create_circle(105, 105, 50, fill="green", outline="#DDD", width=5)
			middle_dot = canvas.create_circle(105, 105, 5, fill="white", outline="#DDD", width=0)
		
		canvas.grid(sticky = 'nswe')
		content.grid(sticky = 'nswe')
		make_dynamic(root)
		make_dynamic(content)
		
		#{{{{{{{{{self widget attributes}}}}}}}}}#
		
		self.root = root
		self.content = content
		self.color_circle = color_circle
		self.transparent_circle = transparent_circle
		self.middle_dot = middle_dot

		self.canvas = canvas
		self.callback = callback
		self.configure_widgets()

		
		root.title("picker_window")
		root.update()
		#root.minsize(root.winfo_width(), root.winfo_height())
		def test(event):
			root.geometry('100x100')
			#root.update()
			#canvas.delete(middle_dot)
			#self.middle_dot =  canvas.create_circle(250, 250, 5, fill="white", outline="#DDD", width=0)
		root.bind('<t>',test)
		root.bind("<Configure>",lambda event:print(event))
		#root.mainloop()

	def configure_widgets(self):
		self.listener = Listener(on_move = self.on_mouse_move,on_click = self.on_click)
		self.listener.start()
		
		self.canvas.config(bg=RGB_to_HEX(self.transparent_color))
		self.canvas.itemconfig(self.transparent_circle ,fill =RGB_to_HEX(self.transparent_color))

		#self.root.wm_attributes('-transparentcolor',RGB_to_HEX(self.transparent_color))
		self.root.bind('<Control-e>', self.test)
		self.root.bind('<Control-E>',self.test)
		#self.root.bind('<KeyRelease>', self.key_release_handler)

	def test(self,event):

		if self.maginfier_on :
			self.stop_magnifier()
		else:
			self.start_magnifier()
	def stop_magnifier(self):
		self.maginfier_on = False
		if self.canvas_img:
				self.canvas.delete(self.canvas_img)
				self.canvas_img = None
	def start_magnifier(self):
		self.maginfier_on = True
		x,y = mouse.position
		size = 10
		monitor = {"top": y-size//2, "left": x-size//2, "width": size, "height": size }
		arr = np.array(sct.grab(monitor))
		arr = BGR_to_RGB(arr[:,:,:-1])
		self.img =  ImageTk.PhotoImage(Image.fromarray(arr).resize((100,100),0))
		self.canvas_img = self.canvas.create_image(100, 100, anchor="center", image=self.img)

	def key_press_handler(self,event):
		pass#key = print(event.keysym)

	def key_release_handler(self,event):
		pass#print(event)


	def on_click(self,x,y,*args):
		self.canvas.itemconfig(self.middle_dot ,fill =RGB_to_HEX(self.transparent_color) )
		self.root.update()
		pix = get_pix(x,y)
		self.canvas.itemconfig(self.middle_dot ,fill ='white')
		self.root.update()

		self.callback(pix)
		self.listener.stop()
		self.root.destroy()

	def on_mouse_move(self,x,y):
		try:
			cx,cy = self.canvas.width//2,self.canvas.height//2
			change_position(self.root,x-cx,y-cy)
		except:
			return

		self.root.config(cursor = 'none')
		self.canvas.itemconfig(self.middle_dot ,fill =RGB_to_HEX(self.transparent_color) )
		self.root.update()
		
		if self.maginfier_on:
			if self.canvas_img:
				self.canvas.delete(self.canvas_img)
				self.canvas_img = None
				self.start_magnifier()


		pix = get_pix(x,y)
		self.canvas.itemconfig(self.middle_dot ,fill ='white')
		self.root.config(cursor = 'cross')
		self.root.update()
		if pix in  (PickerWindow.transparent_color, PickerWindow.transparent_color_backup):
			l = [PickerWindow.transparent_color, PickerWindow.transparent_color_backup]
			l.remove(pix)
			self.transparent_color = l[0]
			self.root.wm_attributes('-transparentcolor',RGB_to_HEX(self.transparent_color))
			self.canvas.itemconfig(self.transparent_circle ,fill =RGB_to_HEX(self.transparent_color) )
			self.canvas.config(bg =RGB_to_HEX(self.transparent_color) )

		hexx_value = RGB_to_HEX(pix)
		self.canvas.itemconfig(self.color_circle,fill =hexx_value )
		

class App(object):
	pos = None
	listener = None
	pix = None
	output_type = 'rgb'
	output_format = '0-255'
	def __init__(self,root):
		font = ('',15,'bold')
		content = tk.Frame(root)
		if content:
			frame = tk.LabelFrame(content, text="RGB Color Picker",font = ('',12,''))
			if frame:
				f00 = tk.Frame(frame)
				if f00:
					pick_button=  tk.Button(f00, text="Pick Color",font = font)
					rgb_hex_button =  tk.Button(f00, text="RGB",font = font)
					copy_button = tk.Button(f00,text = 'Copy',font = font)
					percent_button = tk.Button(f00,text = 'percent',font = font)

			frame2 = tk.LabelFrame(content, text="",highlightthickness=0,borderwidth = 0)
			if frame2:
				entree = tk.Entry(frame2,width=5,font = font)
				color_box = tk.Frame(frame2, bg="red",highlightthickness=1, highlightbackground="black",width = 30,height = 30)
				
		content.grid(sticky = 'nswe',padx = 5,pady=(0,2))
		frame.grid(sticky = 'nswe')
		f00.grid(sticky = 'nw',padx = 5,pady = (1,5))
		pick_button.grid(sticky = '',padx = (0,2))
		rgb_hex_button.grid(row =0,column=1,sticky = '')
		copy_button.grid(row =0,column = 2,sticky = '')
		percent_button.grid(row =0,column = 3,sticky = '')
		
		frame2.grid(sticky = 'nswe',pady = (3,2))
		entree.grid(sticky = 'news')
		color_box.grid(row = 0,column = 1,sticky = '')

		make_dynamic(root)
		make_dynamic(content,rows = (0,))
		make_dynamic(frame)
		#make_dynamic(f00,uniform = False)
		make_dynamic(frame2,rows=(),columns = (0,))

		#{{{{{{{{{self widget attributes}}}}}}}}}#
		self.root = root
		self.pick_button = pick_button
		self.color_box = color_box
		self.rgb_hex_button = rgb_hex_button
		self.output_entry = entree
		self.copy_button = copy_button
		self.percent_button = percent_button
		self.configure_widgets()

		root.title("Color Picker")
		root.update()
		root.minsize(root.winfo_width(), root.winfo_height())
		root.mainloop()

	def configure_widgets(self):
		self.pick_button.configure(command = self.pick_button_command)
		self.rgb_hex_button.configure(command = self.rgb_hex_button_command)
		self.copy_button.config(command = self.copy_to_clipboard)
		self.percent_button.config(command = self.switch_to_percentage)
		self.output_entry_var = tk.StringVar() ; self.output_entry_var.set("nyes")
		self.output_entry.configure(textvariable = self.output_entry_var)
		self.output_entry.bind("<FocusIn>", lambda event:self.output_entry.selection_range(0, tk.END))
		self.output_entry['state'] = 'readonly'
		#self.output_entry.bind('<Double-Button-1>', lambda event:self.output_entry.selection_range(0, tk.END))
	def switch_to_percentage(self):
		if self.output_format == '0-255':
			self.output_format = '0-1'
			self.update_output(percentage_format= True)
		else:
			self.output_format = '0-255'
			self.update_output(percentage_format= False)

	def copy_to_clipboard(self):
		out = self.get_output()
		if out:
			self.root.clipboard_clear()
			self.root.clipboard_append(str(out))
	def bring2front(self):
		self.root.attributes("-topmost", True)
		self.root.attributes("-topmost", False)
		self.root.focus()
	def rgb_hex_button_command(self):
		self.output_type = 'hex' if self.output_type == 'rgb' else 'rgb'
		self.rgb_hex_button.configure(text = self.output_type.upper())
		if self.pix:
			self.update_output()
	def get_output(self):
		return self.output_entry_var.get()
		"""
		if self.pix:
			if self.output_type == 'rgb':
				return self.pix
			if self.output_type == 'hex':
				return RGB_to_HEX(self.pix)
		"""
	def pick_button_command(self):
		if not self.pick_button["state"] == 'disabled':
			self.pick_button["state"] ="disabled"
			self.root.after(200,self.get_mouse_click)
	
	def get_mouse_click(self):
		root = self.root
		top = tk.Toplevel(root)
		topapp = PickerWindow(top,callback = self.set_pix)
		top.focus()
		x,y = root.winfo_x(),root.winfo_y() 
		top.update()

		


	def set_pix(self,pix):
		self.pix = pix
		self.root.after(10,self.bring2front)
		self.root.after(0,self.update_output)
		self.root.after(75, lambda :self.pick_button.configure(state = "normal")) 

	def update_output(self,percentage_format = False):
		hexx_value = '#%02x%02x%02x' % self.pix 
		rgb_value = str(self.pix)
		if percentage_format:
			rgb_value = str(tuple((round(i/255,2) for i in self.pix)))
		self.output_entry_var.set(hexx_value if self.output_type == 'hex' else rgb_value) 
		self.color_box.configure(bg=hexx_value)
		
	

if __name__ == '__main__':
	# load and set the program icon     
	import tempfile ,base64,os
	from my_icon import icon_base64 as icon
	icondata= base64.b64decode(icon)
	tempFile = 'icon.ico'
	tempDir = tempfile.TemporaryDirectory()
	tempFile = tempDir.name + '\\'+tempFile
	print(tempFile)
	iconfile= open(tempFile,"wb")
	iconfile.write(icondata)
	iconfile.close()
	##########

	root = tk.Tk()
	root.wm_iconbitmap(tempFile)

	app = App(root)
	app.tempDir = tempDir
	

	

