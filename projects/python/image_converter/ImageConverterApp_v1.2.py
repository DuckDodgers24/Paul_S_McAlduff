import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk, messagebox, filedialog
from PIL import Image,ImageSequence, UnidentifiedImageError
import pillow_avif
import pillow_heif
pillow_heif.register_heif_opener()
import os

class ImageConverterApp:
    """
    A GUI application for converting images between different formats.

    Supports reading PNG, JPEG, GIF, TIFF, WebP, BMP, HEIF, HEIC and AVIF formats.
    Converts to PNG, JPEG, WebP, GIF, or TIFF with validation for transparency 
    and animation support.
    """

    # Class constants
    MAX_FILENAME_LENGTH = 200
    FORMATS = ["PNG (*.png)",
               "JPEG (*.jpg)",
               "WebP (*.webp)",
               "GIF (*.gif)",
               "TIFF (*.tiff)"]
    
    def __init__(self, root):
        """
        Initialize the Image Converter application.
        
        Args:
            root: The tkinter root window
        """
        
        self.root = root 
        self.root.title("Image Converter")
        self.root.geometry("600x660")
        
        # Initializes instance variables
        self.new_format = "png" # Defaults to .png
        self.input_file_paths = ()
        self.folder_path = ()
        self.remove_all_animation_transparency = False        
        self.remove_animation_transparency = None
        self.remove_all_animation = False
        self.remove_animation = None
        self.remove_all_transparency = False
        self.remove_transparency = None
        self.webp_gif_all_transparency = False
        self.webp_gif_transparency = None
        
        # Builds the UI
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        name_label = ttk.Label(main_frame, text="Image Converter", font=("Arial", 18, "bold"))
        name_label.pack(pady=(20,16))

        main_labelframe = ttk.LabelFrame(main_frame, text="Convert Images")
        main_labelframe.pack()

        select_format_label = ttk.Label(main_labelframe, text="Choose output format", font=("Arial", 12))
        select_format_label.pack(pady=(16,4))

        output_format = ttk.Combobox(main_labelframe, values=self.FORMATS, state="readonly", width=14)
        output_format.pack()
        output_format.current(0) # Selects first item by default
     
        def on_select(event):
            """Handle output format selection from combobox."""            
            selected_format = output_format.get()
            if selected_format == "PNG (*.png)":
                self.new_format = "png"
            elif selected_format == "JPEG (*.jpg)":
                self.new_format = "jpg"
            elif selected_format == "WebP (*.webp)":
                self.new_format = "webp"                
            elif selected_format == "GIF (*.gif)":
                self.new_format = "gif"
            elif selected_format == "TIFF (*.tiff)":
                self.new_format = "tiff"

        output_format.bind("<<ComboboxSelected>>", on_select)
        
        separator_one = ttk.Separator(main_labelframe, orient="horizontal")
        separator_one.pack(fill="x", padx= 80, pady=(26, 20))

        get_image_label = ttk.Label(main_labelframe, text="Select files or drag and drop", font=("Arial", 12))
        get_image_label.pack(pady=(0,4))

        get_image_button = ttk.Button(main_labelframe, text="Browse", command=self.get_image)
        get_image_button.pack()

        # Creates listbox with scrollbar
        listbox_frame = ttk.Frame(main_labelframe)
        listbox_frame.pack(padx= 24, pady=(4,24))

        self.listbox = tk.Listbox(listbox_frame, width=50, height=10, selectmode="extended", font=("Arial", 12))
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)

        self.listbox.config(yscrollcommand=scrollbar.set) # Links listbox and scrollbar

        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Adds drag and drop to listbox
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.add_to_listbox)
     
        # Creates buttons
        button_frame = ttk.Frame(main_labelframe)
        button_frame.pack()

        remove_button = ttk.Button(button_frame, text="Remove Selected", command=self.delete_listbox_item, width=16)
        remove_button.pack(side=tk.LEFT, padx=10)

        clear_button = ttk.Button(button_frame, text="Clear List", command=self.reset_selections, width=16)
        clear_button.pack(side=tk.LEFT, padx=10)

        separator_two = ttk.Separator(main_labelframe, orient="horizontal")
        separator_two.pack(fill="x", padx= 80, pady=(24, 20))

        convert_image_button = ttk.Button(main_labelframe, text="Convert Images", command=self.convert_image)
        convert_image_button.pack(pady=(0, 20))

        exit_button = ttk.Button(main_frame, text="Exit", command=self.confirm_exit) # Closes GUI and ends program
        exit_button.pack(pady=20)


    def add_to_listbox(self, event):
        """
        Handles dropped files and processes them

        Gets the full file paths of dropped images and returns a tuple of strings.
        """
        self.input_file_paths = self.root.tk.splitlist(event.data) # Parses raw data into a tuple of file paths
        if self.input_file_paths:
            self.process_files()

    def get_image(self):
        """
        Opens file dialog and processes selected files
        
        Gets the full file paths of selected images and returns a tuple of strings.
        """
        self.input_file_paths = filedialog.askopenfilenames(
            title="Open",
            filetypes=[("image files", "*.png *.jpg *.jpeg *.jpe *.gif *.tiff *.tif *.webp *.bmp *.heif *.heic *.avif")]
        )
        if self.input_file_paths:
            self.process_files()        

    def process_files(self):
        """      
        Validates filenames to ensure they don't exceed the maximum length.
        Displays valid filenames in the listbox and stores their paths.
        """

        self.listbox.delete(0, tk.END) # Clears listbox before adding files

        valid_paths = []
        
        for input_file_path in self.input_file_paths:
            file_name = os.path.basename(input_file_path)
            base_name = os.path.splitext(file_name)[0]

            # Checks for overly long filename
            if len(base_name) > self.MAX_FILENAME_LENGTH:
                messagebox.showwarning("Warning", "Filenames cannot exceed 200 characters.")
                continue
                
            # Adds filenames to listbox if they are not too long
            valid_paths.append(input_file_path)
            self.listbox.insert(tk.END, file_name)

        # Update with only the valid file paths
        self.input_file_paths = tuple(valid_paths)

    def delete_listbox_item(self):
        """
        Remove selected items from the listbox and file paths.
        
        Updates both the visual listbox display and the stored file paths
        to keep them synchronized.
        """
        
        selected = self.listbox.curselection()
         
        file_paths_list = list(self.input_file_paths)
        
        for index in reversed(selected):
            self.listbox.delete(index)
            file_paths_list.pop(index)

        self.input_file_paths = tuple(file_paths_list)

    def reset_selections(self):
        """
        Clear all items from the listbox and reset file paths.
        
        Removes all entries from the visual listbox and clears the stored
        file paths, returning to an empty state.
        """
        
        self.listbox.delete(0, tk.END)
        self.input_file_paths = ()
        
    def convert_image(self):
        """
        Convert selected images to the chosen output format.
        
        Validates each image for format compatibility (transparency, animation),
        converts compatible images, and saves them to the output folder.
        Opens the output folder when conversion is complete.
        
        Raises:
            Shows error dialog if no images are selected.
            Shows warning dialog if image format is incompatible with output format.
        """

        if not self.input_file_paths:
            messagebox.showerror("Error", "No images have been selected.")
            return
        
        # Prompts user to select an output folder
        self.folder_path = filedialog.askdirectory(
            title="Choose output folder",
            initialdir=os.path.join(os.path.expanduser("~"), "Pictures")
        )
      
        for input_file_path in self.input_file_paths:
            file_name = os.path.basename(input_file_path)
            display_name = file_name[:50] + ("..." if len(file_name) > 50 else "")
            split_name = os.path.splitext(file_name)
            base_name = split_name[0]
            extension_type = split_name[1].lower()
            
            try:
                img = Image.open(input_file_path) # Stores a working copy of the image
            except (UnidentifiedImageError, OSError):
                messagebox.showerror("Invalid File", f"'{file_name}' is not a valid image file.")
                continue

            # Initializes check variables
            img_transparency = False
            img_animation = False

            # Checks for transparent and animated images
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img_transparency = True
            if hasattr(img, 'is_animated') and img.is_animated:
                img_animation = True

            # Chaekc for and processes transparency and animation for JPG and TIFF conversions            
            if img_transparency == True and img_animation == True and self.new_format in ("jpg", "jpeg", "tiff", "tif"):
                if self.remove_all_animation_transparency == False:
                    self.remove_animation_transparency_choice(display_name)  
                if self.remove_animation_transparency != True:
                    continue

                img.seek(0)  # Go to first frame
                img = img.copy()  # Make a copy of the first frame

                if img.mode in ('RGBA', 'LA'):
                    # Converts png and webp images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background

                elif img.mode == 'P':
                    # Converts gif images
                    img = img.convert('RGBA')
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background

            # Chaekc for and processes transparency and animation for GIF conversions
            elif img_animation == True and img_animation == True and self.new_format == "gif":
                if self.remove_all_animation_transparency == False:
                    self.remove_animation_transparency_choice(display_name)  
                if self.remove_animation_transparency != True:
                    continue
                    
                img.seek(0)
                img = img.convert("RGBA")
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            # Chaekc for and processes animated conversions
            elif img_animation == True and self.new_format != "gif":
                if self.remove_all_animation == False:
                    self.remove_animation_choice(display_name)            
                if self.remove_animation != True:
                    continue

                img.seek(0)  # Go to first frame
                img = img.copy()  # Make a copy of the first frame
        
            # Chaekc for and processes transparency to JPG and TIFF conversions            
            elif img_transparency == True and self.new_format in ("jpg", "jpeg", "tiff", "tif"):
                if self.remove_all_transparency == False:
                    self.remove_transparency_choice(display_name)  
                if self.remove_transparency != True:
                    continue

                if img.mode in ('RGBA', 'LA'):
                    # Converts png and webp images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background

                elif img.mode == 'P':
                    # Converts gif images
                    img = img.convert('RGBA')
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background

            # Chaekc for and processes transparent WebP to GIF conversions            
            elif img_transparency == True and extension_type == ".webp" and self.new_format == "gif":
                if self.webp_gif_all_transparency == False:
                    self.webp_gif_transparency_choice(display_name)  
                if self.webp_gif_transparency != True:
                    continue

            output_file_path = os.path.join(self.folder_path, f"{base_name}.{self.new_format}")

            # Converts image to RGB for JPG conversions
            if self.new_format in ("jpg", "jpeg", "tiff", "tif"):
                img = img.convert('RGB')

            # Converts image to RGBA for WebP conversions
            if img.mode == 'P' and self.new_format == "webp":
               img = img.convert('RGBA')     
                
            # Saves converted image to disk drive
            img.save(output_file_path)

        self.reset_selections()

        self.remove_all_animation_transparency = False        
        self.remove_animation_transparency = None
        self.remove_all_animation = False
        self.remove_animation = None
        self.remove_all_transparency = False
        self.remove_transparency = None
        self.webp_gif_all_transparency = False
        self.webp_gif_transparency = None
        
        # Opens output folder 
        os.startfile(self.folder_path)

    def remove_animation_transparency_choice(self, current_file_name):
        """
        Display popup for animated images with transparency being converted to JPEG/TIFF or GIF.
    
        Shows warning that both animation and transparency will be removed during conversion.
        Includes checkbox to apply choice to all remaining files with same conflict.
    
        Args:
            current_file_name (str): Name of the current file being processed
        
        Sets:
            self.remove_animation_transparency (bool): True to proceed, False to skip, None if closed
            self.remove_all_animation_transparency (bool): True if "Apply to all" checked
        """
        
        remove_animation_transparency_popup = tk.Toplevel(self.root)

        # Configure the window
        remove_animation_transparency_popup.title("Animation and Transparency Conversions")
        remove_animation_transparency_popup.geometry("430x230")
        remove_animation_transparency_popup.transient(self.root)
        remove_animation_transparency_popup.grab_set()

        main_frame = ttk.Frame(remove_animation_transparency_popup)
        main_frame.pack()

        title_label = ttk.Label(main_frame, text="Animation and Transparency Conversions", font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 14))

        text_label = ttk.Label(main_frame, text=f"Converting: {current_file_name}\n\nAnimation and transparency will be removed during this conversion.\nDo you wish to proceed?")
        text_label.pack()

        def on_yes():
            """User clicks OK to proceed with conversion."""
            self.remove_animation_transparency = True
            self.remove_all_animation_transparency = var.get()
            remove_animation_transparency_popup.destroy()
        
        def on_no():
            """User clicks Cancel to skip this file."""
            self.remove_animation_transparency = False
            self.remove_all_animation_transparency = var.get()
            remove_animation_transparency_popup.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=14)

        remove_button = ttk.Button(button_frame, text="OK", command=on_yes, width=10)
        remove_button.pack(side=tk.LEFT, padx=10)

        clear_button = ttk.Button(button_frame, text="Cancel", command=on_no, width=10)
        clear_button.pack(side=tk.LEFT, padx=10)

        var = tk.BooleanVar()

        remove_all_check = ttk.Checkbutton(
            main_frame,
            text="Apply to all",       
            variable=var,               
        )
        remove_all_check.pack(pady=(0, 14))

        remove_animation_transparency_popup.wait_window()


    def remove_animation_choice(self, current_file_name):
        """
        Display popup for animated images being converted to formats that don't support animation.
    
        Shows warning that animation will be removed (first frame extracted).
        Includes checkbox to apply choice to all remaining animated files.
    
        Args:
            current_file_name (str): Name of the current file being processed
        
        Sets:
            self.remove_animation (bool): True to proceed, False to skip, None if closed
            self.remove_all_animation (bool): True if "Apply to all" checked
        """
        
        remove_animation_popup = tk.Toplevel(self.root)

        # Configure the window
        remove_animation_popup.title("Animation Conversions")
        remove_animation_popup.geometry("430x230")
        remove_animation_popup.transient(self.root)
        remove_animation_popup.grab_set()

        main_frame = ttk.Frame(remove_animation_popup)
        main_frame.pack()

        title_label = ttk.Label(main_frame, text="Animation Conversions", font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 14))

        text_label = ttk.Label(main_frame, text=f"Converting: {current_file_name}\n\nAnimation will be removed during this conversion.\nDo you wish to proceed?")
        text_label.pack()

        def on_yes():
            """User clicks OK to proceed with conversion."""
            self.remove_animation = True
            self.remove_all_animation = var.get()
            remove_animation_popup.destroy()
  
        def on_no():
            """User clicks Cancel to skip this file."""
            self.remove_animation = False
            self.remove_all_animation = var.get()
            remove_animation_popup.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=14)

        remove_button = ttk.Button(button_frame, text="OK", command=on_yes, width=10)
        remove_button.pack(side=tk.LEFT, padx=10)

        clear_button = ttk.Button(button_frame, text="Cancel", command=on_no, width=10)
        clear_button.pack(side=tk.LEFT, padx=10)

        var = tk.BooleanVar()

        remove_all_check = ttk.Checkbutton(
            main_frame,
            text="Apply to all",       
            variable=var,               
        )
        remove_all_check.pack(pady=(0, 14))

        remove_animation_popup.wait_window()

    def remove_transparency_choice(self, current_file_name):
        """
        Display popup for transparent images being converted to JPEG or TIFF.
    
        Shows warning that transparency will be removed (replaced with white background).
        Includes checkbox to apply choice to all remaining transparent files.
    
        Args:
            current_file_name (str): Name of the current file being processed
        
        Sets:
            self.remove_transparency (bool): True to proceed, False to skip, None if closed
            self.remove_all_transparency (bool): True if "Apply to all" checked
        """
        
        remove_transparency_popup = tk.Toplevel(self.root)

        # Configure the window
        remove_transparency_popup.title("Transparency Conversions")
        remove_transparency_popup.geometry("430x230")
        remove_transparency_popup.transient(self.root)
        remove_transparency_popup.grab_set()

        main_frame = ttk.Frame(remove_transparency_popup)
        main_frame.pack()

        title_label = ttk.Label(main_frame, text="Transparency Conversions", font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 14))

        text_label = ttk.Label(main_frame, text=f"Converting: {current_file_name}\n\nTransparency will be removed during this conversion.\nDo you wish to proceed?")
        text_label.pack()

        def on_yes():
            """User clicks OK to proceed with conversion."""
            self.remove_transparency = True
            self.remove_all_transparency = var.get()
            remove_transparency_popup.destroy()

        def on_no():
            """User clicks Cancel to skip this file."""
            self.remove_transparency = False
            self.remove_all_transparency = var.get()
            remove_transparency_popup.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=14)

        remove_button = ttk.Button(button_frame, text="OK", command=on_yes, width=10)
        remove_button.pack(side=tk.LEFT, padx=10)

        clear_button = ttk.Button(button_frame, text="Cancel", command=on_no, width=10)
        clear_button.pack(side=tk.LEFT, padx=10)

        var = tk.BooleanVar()

        remove_all_check = ttk.Checkbutton(
            main_frame,
            text="Apply to all",       
            variable=var,               
        )
        remove_all_check.pack(pady=(0, 14))

        remove_transparency_popup.wait_window()

    def webp_gif_transparency_choice(self, current_file_name):
        """
        Display popup for WebP to GIF conversions with transparency.
    
        Shows quality warning about GIF's limited transparency and color support.
        Includes checkbox to apply choice to all remaining WebP to GIF conversions.
    
        Args:
            current_file_name (str): Name of the current file being processed
        
        Sets:
            self.webp_gif_transparency (bool): True to proceed, False to skip, None if closed
            self.webp_gif_all_transparency (bool): True if "Apply to all" checked
        """
        
        webp_gif_transparency_popup = tk.Toplevel(self.root)

        # Configure the window
        webp_gif_transparency_popup.title("WebP to GIF Conversions")
        webp_gif_transparency_popup.geometry("430x230")
        webp_gif_transparency_popup.transient(self.root)
        webp_gif_transparency_popup.grab_set()

        main_frame = ttk.Frame(webp_gif_transparency_popup)
        main_frame.pack()

        title_label = ttk.Label(main_frame, text="WebP to GIF Conversions", font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 14))

        text_label = ttk.Label(main_frame, text=f"Converting: {current_file_name}\n\nQuality may be reduced during WebP to GIF conversions.\nDo you wish to proceed?")
        text_label.pack()

        def on_yes():
            """User clicks OK to proceed with conversion."""
            self.webp_gif_transparency = True
            self.webp_gif_all_transparency = var.get()
            webp_gif_transparency_popup.destroy()

        def on_no():
            """User clicks Cancel to skip this file."""
            self.webp_gif_transparency = False
            self.webp_gif_all_transparency = var.get()
            webp_gif_transparency_popup.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=14)

        remove_button = ttk.Button(button_frame, text="OK", command=on_yes, width=10)
        remove_button.pack(side=tk.LEFT, padx=10)

        clear_button = ttk.Button(button_frame, text="Cancel", command=on_no, width=10)
        clear_button.pack(side=tk.LEFT, padx=10)

        var = tk.BooleanVar()

        remove_all_check = ttk.Checkbutton(
            main_frame,
            text="Apply to all",       
            variable=var,               
        )
        remove_all_check.pack(pady=(0, 14))

        webp_gif_transparency_popup.wait_window()
 
 
    def confirm_exit(self):
        """
        Show confirmation dialog before closing the application.
        
        Prompts user to confirm exit and destroys the application window
        if confirmed.
        """
        
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            self.root.destroy()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ImageConverterApp(root)
    root.mainloop()
